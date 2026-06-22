import hashlib
import os
from werkzeug.security import generate_password_hash, check_password_hash

# ---------- USER MODEL ----------
class User:
    def __init__(self, username, email, password, role='user'):
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.role = role
        self.api_key = hashlib.sha256(os.urandom(16)).hexdigest()[:16]

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def regenerate_api_key(self):
        self.api_key = hashlib.sha256(os.urandom(16)).hexdigest()[:16]
        return self.api_key

# ---------- DATABASES (in-memory) ----------
users_db = {}          # username -> User object
results_db = []        # list of dicts: {account, status, detail}
stats = {'success': 0, 'failed': 0, 'invalid': 0, 'errors': 0}
proxies_list = []
combo_lines = []

# ---------- HELPERS ----------
def add_result(account, status, detail):
    results_db.append({'account': account, 'status': status, 'detail': detail})

def update_stats(status):
    stats[status] = stats.get(status, 0) + 1