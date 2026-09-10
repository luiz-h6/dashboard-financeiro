import os

app_js_path = r"c:\Users\luiz_\Desktop\dashboard financeiro\frontend\js\app.js"

with open(app_js_path, 'r', encoding='utf-8') as f:
    content = f.read()

sync_logic = """
// Botão de Sincronizar Mercado
const btnSyncApi = document.getElementById('btnSyncApi');
if(btnSyncApi) {
    btnSyncApi.addEventListener('click', async () => {
        btnSyncApi.textContent = 'Sincronizando...';
        btnSyncApi.classList.add('opacity-50', 'cursor-not-allowed');
        
        try {
            const res = await fetch(`${API_BASE}/investments/sync-prices`, {
                method: 'POST',
                headers: getAuthHeaders()
            });
            const data = await res.json();
            
            if(res.ok) {
                alert(`Mercado Sincronizado!\\n${data.updated} ativos atualizados.`);
                loadDashboard(); // Recarrega os KPIs
            } else {
                alert('Erro ao sincronizar: ' + (data.error || 'Desconhecido'));
            }
        } catch(err) {
            alert('Erro de conexão com o servidor ao sincronizar.');
        } finally {
            btnSyncApi.textContent = 'Sincronizar Mercado';
            btnSyncApi.classList.remove('opacity-50', 'cursor-not-allowed');
        }
    });
}
"""

if 'btnSyncApi.addEventListener' not in content:
    content = content + "\n\n" + sync_logic
    with open(app_js_path, 'w', encoding='utf-8') as f:
        f.write(content)
        print("Botão sincronizar arrumado!")
