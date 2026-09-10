import os

app_js_path = r"c:\Users\luiz_\Desktop\dashboard financeiro\frontend\js\app.js"

with open(app_js_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add Auth Check and Headers helper
auth_code = """
// ==========================================
// AUTENTICAÇÃO E SEGURANÇA
// ==========================================
const token = localStorage.getItem('token');
if (!token) {
    window.location.href = 'login.html';
}

function getAuthHeaders() {
    return { 'Authorization': 'Bearer ' + token };
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('userName');
    window.location.href = 'login.html';
}

// Configurar nome do usuário no topo
document.addEventListener('DOMContentLoaded', () => {
    const userName = localStorage.getItem('userName');
    if(userName) {
        const el = document.getElementById('topUserName');
        if(el) el.textContent = userName.split(' ')[0];
    }
});

"""

if "AUTENTICAÇÃO E SEGURANÇA" not in content:
    content = auth_code + content

# 2. Replace 'X-User-Id': '1'
content = content.replace("{ 'X-User-Id': '1' }", "getAuthHeaders()")
content = content.replace("{ 'X-User-Id': '1', 'Content-Type': 'application/json' }", "{ ...getAuthHeaders(), 'Content-Type': 'application/json' }")

with open(app_js_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("app.js patched.")
