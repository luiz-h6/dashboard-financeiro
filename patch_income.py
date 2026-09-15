import os
import re

base_dir = r"c:\Users\luiz_\Desktop\dashboard financeiro"

# 1. Update index.html
index_path = os.path.join(base_dir, "frontend", "index.html")
with open(index_path, 'r', encoding='utf-8') as f:
    html = f.read()

if 'id="container_flags"' not in html:
    html = html.replace(
        '<div class="pt-4 border-t border-slate-700 grid grid-cols-1 sm:grid-cols-2 gap-4">',
        '<div id="container_flags" class="pt-4 border-t border-slate-700 grid grid-cols-1 sm:grid-cols-2 gap-4">'
    )
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html)

# 2. Update app.js
app_js_path = os.path.join(base_dir, "frontend", "js", "app.js")
with open(app_js_path, 'r', encoding='utf-8') as f:
    appjs = f.read()

# Substituir a função toggleFormMode inteira
new_toggle = """function toggleFormMode() {
    const type = document.querySelector('input[name="type"]:checked').value;
    const catContainer = document.getElementById('container_category');
    const transContainer = document.getElementById('container_transfer');
    const instContainer = document.getElementById('container_installments');
    const flagsContainer = document.getElementById('container_flags');
    const labelAcc = document.getElementById('label_account_id');
    const catSelect = document.getElementById('category_id');

    // Atualiza opções de categoria baseadas no tipo selecionado
    if (catSelect && allCategories) {
        catSelect.innerHTML = '<option value="0">N/A (Sem Categoria)</option>';
        allCategories.filter(c => c.type === type || type === 'transfer').forEach(c => { 
            catSelect.innerHTML += `<option value="${c.id}">${c.name}</option>`; 
        });
    }

    if (type === 'transfer') {
        catContainer.classList.add('hidden');
        document.getElementById('category_id').required = false;
        transContainer.classList.remove('hidden');
        document.getElementById('transfer_account_id').required = true;
        instContainer.classList.add('hidden');
        if (flagsContainer) flagsContainer.classList.add('hidden');
        labelAcc.innerText = "Conta (Origem)";
    } else {
        catContainer.classList.remove('hidden');
        document.getElementById('category_id').required = false; // Permite N/A
        transContainer.classList.add('hidden');
        document.getElementById('transfer_account_id').required = false;
        
        if (type === 'expense') {
            instContainer.classList.remove('hidden');
            if (flagsContainer) flagsContainer.classList.remove('hidden');
        } else {
            instContainer.classList.add('hidden');
            if (flagsContainer) flagsContainer.classList.add('hidden');
        }
        labelAcc.innerText = "Conta Financeira";
    }
}"""

# Achar e substituir a velha toggleFormMode
appjs = re.sub(r'function toggleFormMode\(\) \{.*?\n\}', new_toggle, appjs, flags=re.DOTALL)

# Substituir payload logic para enviar 0 se N/A
payload_patch = """        category_id: type === 'transfer' ? null : (parseInt(document.getElementById('category_id').value) || 0),"""
appjs = re.sub(r"category_id: type === 'transfer' \? null : parseInt\(document\.getElementById\('category_id'\)\.value\),", payload_patch, appjs)

with open(app_js_path, 'w', encoding='utf-8') as f:
    f.write(appjs)

# 3. Update backend/models/transaction.py
tx_path = os.path.join(base_dir, "backend", "models", "transaction.py")
with open(tx_path, 'r', encoding='utf-8') as f:
    tx = f.read()

new_tx = """    user_id = data['user_id']
    cat_id = data.get('category_id')
    tx_type = data['type']
    
    # Lidar com Categoria "N/A" (0 ou null)
    if tx_type != 'transfer' and (not cat_id or cat_id == 0):
        cursor.execute("SELECT id FROM categories WHERE user_id = ? AND type = ? AND name = 'Geral'", (user_id, tx_type))
        row = cursor.fetchone()
        if row:
            cat_id = row['id']
        else:
            cursor.execute("INSERT INTO categories (user_id, name, type, color) VALUES (?, ?, ?, ?)", (user_id, 'Geral', tx_type, '#94a3b8'))
            cat_id = cursor.lastrowid

    total_installments = int(data.get('total_installments', 1))"""

tx = re.sub(r"    total_installments = int\(data\.get\('total_installments', 1\)\)", new_tx, tx)

# Arrumar a inserção no SQL
tx = tx.replace("data.get('category_id')", "cat_id")

with open(tx_path, 'w', encoding='utf-8') as f:
    f.write(tx)

print("Patch aplicado com sucesso!")
