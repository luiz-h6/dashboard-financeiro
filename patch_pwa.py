import os
import re

base_dir = r"c:\Users\luiz_\Desktop\dashboard financeiro"
frontend_dir = os.path.join(base_dir, "frontend")

# 1. Update index.html
index_path = os.path.join(frontend_dir, "index.html")
with open(index_path, 'r', encoding='utf-8') as f:
    content = f.read()

head_additions = """
    <link rel="manifest" href="/manifest.json">
    <meta name="theme-color" content="#020617">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
"""
if '<link rel="manifest"' not in content:
    content = content.replace('</title>', '</title>' + head_additions)

sw_registration = """
    <script>
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', () => {
                navigator.serviceWorker.register('/sw.js');
            });
        }
    </script>
"""
if 'navigator.serviceWorker.register' not in content:
    content = content.replace('</body>', sw_registration + '\n</body>')

with open(index_path, 'w', encoding='utf-8') as f:
    f.write(content)


# 2. Update login.html
login_path = os.path.join(frontend_dir, "login.html")
with open(login_path, 'r', encoding='utf-8') as f:
    content = f.read()

if '<link rel="manifest"' not in content:
    content = content.replace('</title>', '</title>' + head_additions)
if 'navigator.serviceWorker.register' not in content:
    content = content.replace('</body>', sw_registration + '\n</body>')

# Change API_BASE in login.html
content = re.sub(r"const API_BASE = 'http://127\.0\.0\.1:5000/api';", "const API_BASE = '/api';", content)
with open(login_path, 'w', encoding='utf-8') as f:
    f.write(content)


# 3. Change API_BASE in app.js
app_js_path = os.path.join(frontend_dir, "js", "app.js")
with open(app_js_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(r"const API_BASE = 'http://127\.0\.0\.1:5000/api';", "const API_BASE = '/api';", content)
with open(app_js_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Frontend PWA files patched.")
