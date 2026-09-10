
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

const API_BASE = 'http://localhost:5000/api';
let allAccounts = [];
let allCategories = [];

// Formatador
const formatCurrency = (value) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);

// ==========================================
// TABS E NAVEGAÇÃO
// ==========================================
function switchTab(tabId) {
    ['dashboard', 'lancamentos', 'historico', 'evolucao', 'budgets'].forEach(id => {
        document.getElementById(`tab-${id}`).classList.add('hidden');
        const btn = document.getElementById(`btn-tab-${id}`);
        btn.classList.replace('text-white', 'text-slate-400');
        btn.classList.replace('border-neon-cyan', 'border-transparent');
        btn.classList.remove('bg-slate-800/50');
    });

    document.getElementById(`tab-${tabId}`).classList.remove('hidden');
    const activeBtn = document.getElementById(`btn-tab-${tabId}`);
    activeBtn.classList.replace('text-slate-400', 'text-white');
    activeBtn.classList.replace('border-transparent', 'border-neon-cyan');
    activeBtn.classList.add('bg-slate-800/50');

    const titleMap = { 
        'dashboard': 'Visão Analítica', 
        'lancamentos': 'Novo Lançamento',
        'historico': 'Histórico e Edição',
        'evolucao': 'Evolução Detalhada',
        'budgets': 'Metas & Orçamentos'
    };
    document.getElementById('headerTitle').textContent = titleMap[tabId];

    if(tabId === 'lancamentos') loadFormDependencies('account_id', 'category_id');
    if(tabId === 'historico') loadHistory();
    if(tabId === 'evolucao') loadEvolution();
    if(tabId === 'budgets') loadBudgets();
}

// ==========================================
// DEPENDÊNCIAS DE FORMULÁRIO (Selects)
// ==========================================
async function fetchGlobals() {
    if(allAccounts.length === 0) {
        const resA = await fetch(`${API_BASE}/accounts/`, { headers: getAuthHeaders() });
        allAccounts = await resA.json();
    }
    if(allCategories.length === 0) {
        const resC = await fetch(`${API_BASE}/categories/`, { headers: getAuthHeaders() });
        allCategories = await resC.json();
    }
}

async function loadFormDependencies(accSelectId, catSelectId) {
    await fetchGlobals();
    const accSelect = document.getElementById(accSelectId);
    accSelect.innerHTML = '<option value="">Selecione uma Conta...</option>';
    allAccounts.forEach(a => { accSelect.innerHTML += `<option value="${a.id}">${a.name}</option>`; });
    
    // Para conta destino (Transferências)
    const transferSelect = document.getElementById('transfer_account_id');
    if(transferSelect) {
        transferSelect.innerHTML = '<option value="">Selecione a Conta Destino...</option>';
        allAccounts.forEach(a => { transferSelect.innerHTML += `<option value="${a.id}">${a.name}</option>`; });
    }

    const catSelect = document.getElementById(catSelectId);
    catSelect.innerHTML = '<option value="">Selecione uma Categoria...</option>';
    allCategories.forEach(c => { catSelect.innerHTML += `<option value="${c.id}">${c.name}</option>`; });
}

function toggleFormMode() {
    const type = document.querySelector('input[name="type"]:checked').value;
    const catContainer = document.getElementById('container_category');
    const transContainer = document.getElementById('container_transfer');
    const instContainer = document.getElementById('container_installments');
    const labelAcc = document.getElementById('label_account_id');

    if (type === 'transfer') {
        catContainer.classList.add('hidden');
        document.getElementById('category_id').required = false;
        transContainer.classList.remove('hidden');
        document.getElementById('transfer_account_id').required = true;
        instContainer.classList.add('hidden');
        labelAcc.innerText = "Conta (Origem)";
    } else {
        catContainer.classList.remove('hidden');
        document.getElementById('category_id').required = true;
        transContainer.classList.add('hidden');
        document.getElementById('transfer_account_id').required = false;
        
        if (type === 'expense') {
            instContainer.classList.remove('hidden');
        } else {
            instContainer.classList.add('hidden');
        }
        labelAcc.innerText = "Conta Financeira";
    }
}

// ==========================================
// INSERIR NOVO LANÇAMENTO
// ==========================================
document.getElementById('formTransaction').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = document.getElementById('btnSubmit');
    btn.textContent = "Processando...";
    
    const type = document.querySelector('input[name="type"]:checked').value;
    const payload = {
        type: type,
        amount: parseFloat(document.getElementById('amount').value),
        date: document.getElementById('date').value,
        description: document.getElementById('description').value,
        account_id: parseInt(document.getElementById('account_id').value),
        category_id: type === 'transfer' ? null : parseInt(document.getElementById('category_id').value),
        transfer_account_id: type === 'transfer' ? parseInt(document.getElementById('transfer_account_id').value) : null,
        total_installments: type === 'expense' ? parseInt(document.getElementById('total_installments').value) : 1,
        is_essential: document.getElementById('is_essential').checked ? 1 : 0,
        is_fixed: document.getElementById('is_fixed').checked ? 1 : 0,
        status: 'paid'
    };

    try {
        await fetch(`${API_BASE}/transactions/`, {
            method: 'POST',
            headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        alert("Salvo com sucesso!");
        e.target.reset();
        toggleFormMode();
        loadDashboard();
        switchTab('dashboard');
    } catch(err) { alert(err.message); } 
    finally { btn.textContent = "Registrar Movimentação"; }
});

// ==========================================
// ABA: HISTÓRICO E EDIÇÃO
// ==========================================
async function loadHistory() {
    const filter = document.getElementById('histFilterMonth').value; // YYYY-MM
    let url = `${API_BASE}/transactions/`;
    if(filter) {
        const [y, m] = filter.split('-');
        url += `?month=${m}&year=${y}`;
    }

    try {
        await fetchGlobals();
        const response = await fetch(url, { headers: getAuthHeaders() });
        let transactions = await response.json();
        
        const tbody = document.getElementById('fullHistoryBody');
        tbody.innerHTML = '';
        
        if (transactions.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" class="py-4 text-center text-slate-500">Nenhum registro encontrado.</td></tr>`;
            return;
        }

        transactions.forEach(t => {
            const date = new Date(t.date).toLocaleDateString('pt-BR');
            const isIncome = t.type === 'income';
            const valClass = isIncome ? 'text-emerald-400' : 'text-slate-300';
            const accName = allAccounts.find(a => a.id === t.account_id)?.name || 'Conta Excluída';
            
            const tr = document.createElement('tr');
            tr.className = "border-b border-slate-700/50 hover:bg-slate-800/30 transition";
            tr.innerHTML = `
                <td class="py-3 text-slate-400">${date}</td>
                <td class="py-3 text-white">${t.description || '-'}</td>
                <td class="py-3 text-slate-500">${accName}</td>
                <td class="py-3 font-mono text-right ${valClass}">${isIncome?'+':'-'} ${formatCurrency(t.amount)}</td>
                <td class="py-3 text-center space-x-3">
                    <button onclick='openEditModal(${JSON.stringify(t)})' class="text-neon-cyan hover:text-white transition">Editar</button>
                    <button onclick='deleteTransaction(${t.id})' class="text-red-400 hover:text-red-300 transition">Excluir</button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch(err) { console.error(err); }
}

async function deleteTransaction(id) {
    if(!confirm("Tem certeza que deseja excluir esta movimentação?")) return;
    try {
        await fetch(`${API_BASE}/transactions/${id}`, { method: 'DELETE', headers: getAuthHeaders()});
        loadHistory();
        loadDashboard(); // atualiza valores por trás
    } catch(err) { alert("Erro ao excluir."); }
}

// Modal Edição
async function openEditModal(t) {
    await loadFormDependencies('edit_account_id', 'edit_category_id');
    document.getElementById('edit_id').value = t.id;
    document.querySelector(`input[name="edit_type"][value="${t.type}"]`).checked = true;
    document.getElementById('edit_amount').value = t.amount;
    document.getElementById('edit_date').value = t.date;
    document.getElementById('edit_description').value = t.description;
    document.getElementById('edit_account_id').value = t.account_id;
    document.getElementById('edit_category_id').value = t.category_id;
    document.getElementById('edit_is_essential').checked = t.is_essential === 1;
    document.getElementById('edit_is_fixed').checked = t.is_fixed === 1;
    
    document.getElementById('editModal').classList.remove('hidden');
}

function closeEditModal() {
    document.getElementById('editModal').classList.add('hidden');
}

document.getElementById('formEditTransaction').addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('edit_id').value;
    const payload = {
        type: document.querySelector('input[name="edit_type"]:checked').value,
        amount: parseFloat(document.getElementById('edit_amount').value),
        date: document.getElementById('edit_date').value,
        description: document.getElementById('edit_description').value,
        account_id: parseInt(document.getElementById('edit_account_id').value),
        category_id: parseInt(document.getElementById('edit_category_id').value),
        is_essential: document.getElementById('edit_is_essential').checked ? 1 : 0,
        is_fixed: document.getElementById('edit_is_fixed').checked ? 1 : 0,
        status: 'paid'
    };

    try {
        await fetch(`${API_BASE}/transactions/${id}`, {
            method: 'PUT',
            headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        closeEditModal();
        loadHistory();
        loadDashboard();
    } catch(err) { alert("Erro ao editar."); }
});


// ==========================================
// ABA: EVOLUÇÃO DETALHADA
// ==========================================
let evolChartInst = null;
let currentEvoType = 'expense';

function setEvolutionType(type) {
    currentEvoType = type;
    document.getElementById('btnEvoExpense').className = type === 'expense' 
        ? "px-3 py-1 rounded text-sm bg-slate-700 text-white transition" 
        : "px-3 py-1 rounded text-sm text-slate-400 hover:text-white transition";
    
    document.getElementById('btnEvoIncome').className = type === 'income' 
        ? "px-3 py-1 rounded text-sm bg-slate-700 text-white transition" 
        : "px-3 py-1 rounded text-sm text-slate-400 hover:text-white transition";

    const catSelect = document.getElementById('evoCategorySelect');
    catSelect.innerHTML = '<option value="all">Todas as Categorias</option>';
    allCategories.filter(c => c.type === type).forEach(c => {
        catSelect.innerHTML += `<option value="${c.id}">${c.name}</option>`;
    });

    loadEvolution();
}

async function loadEvolution() {
    try {
        await fetchGlobals(); 
        if(document.getElementById('evoCategorySelect').options.length <= 1) {
             setEvolutionType(currentEvoType);
             return;
        }

        const year = document.getElementById('evoYearSelect').value;
        const categoryId = document.getElementById('evoCategorySelect').value;
        
        const resT = await fetch(`${API_BASE}/transactions/`, { headers: getAuthHeaders() });
        const allTransactions = await resT.json();

        let filtered = allTransactions.filter(t => t.date.startsWith(year) && t.type === currentEvoType);
        if (categoryId !== 'all') {
            filtered = filtered.filter(t => t.category_id === parseInt(categoryId));
        }

        const monthTotals = Array(12).fill(0);
        filtered.forEach(t => {
            const monthIndex = parseInt(t.date.substring(5, 7)) - 1;
            monthTotals[monthIndex] += t.amount;
        });

        const labels = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
        const ctx = document.getElementById('evolutionChart').getContext('2d');
        if (evolChartInst) evolChartInst.destroy();
        
        const color = currentEvoType === 'expense' ? '#f43f5e' : '#10b981'; // Rose : Emerald
        const labelText = currentEvoType === 'expense' ? 'Despesas (R$)' : 'Renda (R$)';

        evolChartInst = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: labelText,
                    data: monthTotals,
                    backgroundColor: color,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                scales: { x: { grid: { display: false, color: '#334155' } }, y: { grid: { color: '#1e293b' }, beginAtZero: true } }
            }
        });

    } catch(err) { console.error(err); }
}


// ==========================================
// DASHBOARD (DARK MODE)
// ==========================================
let cashflowChartInstance = null;
let categoryChartInstance = null;
Chart.defaults.color = '#94a3b8'; 
Chart.defaults.font.family = "'Inter', sans-serif";

async function loadDashboard() {
    try {
        const response = await fetch(`${API_BASE}/analytics/dashboard`, { headers: getAuthHeaders() });
        const data = await response.json();
        
        if (data.summary) {
            document.getElementById('kpi-balance').textContent = formatCurrency(data.summary.total_current_balance || 0);
        }

        if (data.cashflow && data.cashflow.length > 0) {
            const lastMonth = data.cashflow[data.cashflow.length - 1];
            document.getElementById('kpi-savings').textContent = `${lastMonth.savings_rate_pct || 0}%`;
            document.getElementById('kpi-savings').className = lastMonth.savings_rate_pct >= 0 ? "text-3xl font-bold text-neon-blue mt-2 font-mono" : "text-3xl font-bold text-red-400 mt-2 font-mono";
        }

        if (data.essential_vs_non_essential && data.essential_vs_non_essential.length > 0) {
            const lastMonth = data.essential_vs_non_essential[data.essential_vs_non_essential.length - 1];
            document.getElementById('kpi-ratio').textContent = `${lastMonth.essential_ratio_pct || 0}% Essencial`;
        }

        if (data.forecasting) {
            const f = data.forecasting;
            document.getElementById('kpi-forecast').textContent = formatCurrency(f.projected_balance || 0);
            document.getElementById('kpi-forecast').className = f.projected_balance >= 0 ? "text-2xl font-bold text-amber-400 mt-2 font-mono" : "text-2xl font-bold text-red-400 mt-2 font-mono";
        }

        renderCharts(data);
        
        // Transações Recentes Dashboard
        const resT = await fetch(`${API_BASE}/transactions/`, { headers: getAuthHeaders() });
        const trans = await resT.json();
        const tbody = document.getElementById('dashboardTransactionsBody');
        tbody.innerHTML = '';
        if(trans.length === 0) {
            tbody.innerHTML = `<tr><td colspan="4" class="py-4 text-center text-slate-500">Nenhum registro.</td></tr>`;
        } else {
            trans.slice(0, 6).forEach(t => {
                const date = new Date(t.date).toLocaleDateString('pt-BR');
                const isIncome = t.type === 'income';
                let tags = '';
                if(t.is_fixed) tags += `<span class="ml-2 px-1.5 py-0.5 rounded text-[10px] bg-fuchsia-500/20 text-fuchsia-400 border border-fuchsia-500/30">Fixo</span>`;
                if(t.is_essential) tags += `<span class="ml-1 px-1.5 py-0.5 rounded text-[10px] bg-neon-cyan/20 text-neon-cyan border border-neon-cyan/30">Essencial</span>`;
                if(t.type === 'transfer') {
                    tbody.innerHTML += `
                        <tr class="border-b border-slate-700/50 hover:bg-slate-800/30 transition">
                            <td class="py-3 text-slate-400">${date}</td>
                            <td class="py-3 text-white font-medium">${t.description || 'Transferência'} ${tags}</td>
                            <td class="py-3 text-slate-500">Transferência</td>
                            <td class="py-3 font-mono text-right text-blue-400">${formatCurrency(t.amount)}</td>
                        </tr>
                    `;
                } else {
                    tbody.innerHTML += `
                        <tr class="border-b border-slate-700/50 hover:bg-slate-800/30 transition">
                            <td class="py-3 text-slate-400">${date}</td>
                            <td class="py-3 text-white font-medium">${t.description || '-'} ${tags}</td>
                            <td class="py-3 text-slate-500">${isIncome?'Receita':'Despesa'}</td>
                            <td class="py-3 font-mono text-right ${isIncome ? 'text-emerald-400' : 'text-slate-300'}">${isIncome?'+':'-'} ${formatCurrency(t.amount)}</td>
                        </tr>
                    `;
                }
            });
        }
    } catch (error) { console.error(error); }
}

function renderCharts(data) {
    if (data.cashflow && data.cashflow.length > 0) {
        const labels = data.cashflow.map(item => item.month_year);
        const expenses = data.cashflow.map(item => item.total_expense);
        const balances = data.cashflow.map(item => item.net_balance);

        const ctx1 = document.getElementById('cashflowChart').getContext('2d');
        if (cashflowChartInstance) cashflowChartInstance.destroy();
        
        const gradientBlue = ctx1.createLinearGradient(0, 0, 0, 400);
        gradientBlue.addColorStop(0, 'rgba(6, 182, 212, 0.5)');
        gradientBlue.addColorStop(1, 'rgba(6, 182, 212, 0.0)');

        cashflowChartInstance = new Chart(ctx1, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    { label: 'Saldo Líquido', data: balances, borderColor: '#06b6d4', backgroundColor: gradientBlue, borderWidth: 3, fill: true, tension: 0.4, pointBackgroundColor: '#0f172a', pointBorderColor: '#06b6d4', pointBorderWidth: 2, pointRadius: 4 },
                    { label: 'Despesas', data: expenses, type: 'bar', backgroundColor: 'rgba(244, 63, 94, 0.8)', borderRadius: 4, barPercentage: 0.3 }
                ]
            },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: true, position: 'top' } }, scales: { x: { grid: { display: false, color: '#334155' } }, y: { grid: { color: '#1e293b' }, beginAtZero: true } } }
        });
    }

    if (data.expenses_by_category && data.expenses_by_category.length > 0) {
        const catLabels = data.expenses_by_category.map(item => item.category_name);
        const catValues = data.expenses_by_category.map(item => item.total_amount);
        const paletteDark = ['#06b6d4', '#3b82f6', '#8b5cf6', '#d946ef', '#f43f5e', '#f97316', '#eab308', '#10b981', '#14b8a6', '#6366f1'];
        const ctx2 = document.getElementById('categoryChart').getContext('2d');
        if (categoryChartInstance) categoryChartInstance.destroy();
        categoryChartInstance = new Chart(ctx2, {
            type: 'doughnut',
            data: { labels: catLabels, datasets: [{ data: catValues, backgroundColor: paletteDark.slice(0, catValues.length), borderColor: '#0f172a', borderWidth: 2, hoverOffset: 10 }] },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'right', labels: { boxWidth: 12, color: '#cbd5e1' } } }, cutout: '75%' }
        });
    }
}

// ==========================================
// ABA: METAS E ORÇAMENTOS
// ==========================================
async function loadBudgets() {
    try {
        await fetchGlobals();
        const catSelect = document.getElementById('budget_category_id');
        catSelect.innerHTML = '<option value="">Selecione a Categoria...</option>';
        allCategories.filter(c => c.type === 'expense').forEach(c => {
            catSelect.innerHTML += `<option value="${c.id}">${c.name}</option>`;
        });

        const response = await fetch(`${API_BASE}/analytics/dashboard`, { headers: getAuthHeaders() });
        const data = await response.json();
        const expenses = data.expenses_by_category || [];
        
        const listContainer = document.getElementById('budgetsList');
        listContainer.innerHTML = '';

        expenses.forEach(exp => {
            if(exp.budget_limit > 0) {
                const pct = exp.budget_pct;
                let colorClass = 'bg-emerald-500';
                if(pct > 75) colorClass = 'bg-amber-500';
                if(pct > 100) colorClass = 'bg-red-500';

                listContainer.innerHTML += `
                    <div>
                        <div class="flex justify-between items-center mb-1">
                            <span class="text-sm font-semibold text-white">${exp.category_name}</span>
                            <span class="text-xs text-slate-400">R$ ${exp.total_amount} de R$ ${exp.budget_limit} (${pct}%)</span>
                        </div>
                        <div class="w-full bg-slate-700 rounded-full h-2.5">
                            <div class="${colorClass} h-2.5 rounded-full transition-all" style="width: ${Math.min(pct, 100)}%"></div>
                        </div>
                    </div>
                `;
            }
        });
        
        if(listContainer.innerHTML === '') {
            listContainer.innerHTML = '<p class="text-slate-500 text-sm">Nenhum orçamento definido. Preencha o formulário acima.</p>';
        }

    } catch (err) { console.error(err); }
}

document.getElementById('formBudget').addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
        category_id: parseInt(document.getElementById('budget_category_id').value),
        amount: parseFloat(document.getElementById('budget_amount').value)
    };
    try {
        await fetch(`${API_BASE}/budgets/`, {
            method: 'POST', headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        document.getElementById('budget_amount').value = '';
        loadBudgets();
        loadDashboard();
    } catch(err) { alert(err.message); }
});

document.addEventListener('DOMContentLoaded', loadDashboard);



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
                alert(`Mercado Sincronizado!\n${data.updated} ativos atualizados.`);
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
