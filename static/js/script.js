// Auto-dismiss alerts
setTimeout(() => {
    document.querySelectorAll('.alert').forEach(el => {
        const bs = bootstrap.Alert.getInstance(el);
        if (bs) bs.close();
    });
}, 5000);

// File upload drag & drop enhancement
document.querySelectorAll('.upload-zone').forEach(zone => {
    zone.addEventListener('dragover', e => {
        e.preventDefault();
        zone.classList.add('dragover');
    });
    zone.addEventListener('dragleave', () => zone.classList.remove('dragover'));
    zone.addEventListener('drop', e => {
        e.preventDefault();
        zone.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length) {
            const input = zone.querySelector('input[type="file"]');
            if (input) input.files = files;
        }
    });
});

// Copy API key
function copyKey(elementId) {
    const el = document.getElementById(elementId);
    if (!el) return;
    const text = el.textContent.trim();
    if (!text || text === '—' || text === 'No key generated') return;
    navigator.clipboard.writeText(text).then(() => {
        const toast = new bootstrap.Toast(document.getElementById('copyToast'));
        toast.show();
    }).catch(() => {});
}

// Toggle password visibility
function togglePass(id) {
    const inp = document.getElementById(id);
    if (!inp) return;
    inp.type = inp.type === 'password' ? 'text' : 'password';
}