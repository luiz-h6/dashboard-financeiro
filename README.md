# 📊 Plataforma Web de Controle Financeiro Pessoal

Um sistema financeiro robusto, moderno e totalmente focado na gestão da economia real do seu dia a dia. Construído com Python (Flask), SQLite, Pandas, HTML5 e TailwindCSS.

---

## 🛠️ Requisitos do Sistema

Para rodar o projeto localmente, você precisará ter instalado em sua máquina apenas:
1. **Python 3.8+** (Já vem com o SQLite embutido).
2. **Navegador Web Moderno** (Chrome, Edge, Firefox, etc).

**Bibliotecas Python Utilizadas** (Já configuradas no arquivo `requirements.txt`):
- `Flask`: Para criar a API REST do Backend.
- `Flask-Cors`: Para permitir que o Frontend HTML converse com o Backend sem bloqueios.
- `python-dotenv`: Para carregar as variáveis de segurança (arquivo `.env`).
- `pandas`: Para cálculos financeiros de alta performance, análises de caixa e kpis.
- `yfinance`: Para buscar valores de ações, fundos e criptomoedas diretamente da bolsa em tempo real.
- `requests`: Para chamadas de rede.

---

## 🚀 Como Rodar o Projeto (Passo a Passo)

Siga os passos abaixo no seu terminal (PowerShell, CMD ou VSCode Terminal):

### Passo 1: Acesse a pasta do Backend
Navegue até a pasta `backend` do projeto:
```powershell
cd "c:\Users\luiz_\Desktop\dashboard financeiro\backend"
```

### Passo 2: Crie o Ambiente Virtual (Recomendado)
Para não misturar as bibliotecas com o seu sistema principal, crie um ambiente virtual:
```powershell
python -m venv venv
```

### Passo 3: Ative o Ambiente Virtual
```powershell
# No Windows PowerShell:
.\venv\Scripts\activate
```
*(Quando ativado, você verá `(venv)` no início da linha do terminal)*.

### Passo 4: Instale as Dependências
Instale todas as bibliotecas que listamos acima com um único comando:
```powershell
pip install -r requirements.txt
```

### Passo 5: Ligue a API (Backend)
Inicie o servidor Flask. Como mudamos para SQLite, o banco de dados será gerado sozinho no exato segundo em que o servidor ligar!
```powershell
python app.py
```
*(Aparecerá uma mensagem informando que a aplicação está rodando em `http://127.0.0.1:5000`)*

### Passo 6: Abra o Aplicativo (Frontend)
Não é necessário nenhum servidor complexo para o visual. 
1. Vá até a pasta `frontend`.
2. Dê **dois cliques** no arquivo `index.html`. Ele abrirá no seu navegador com o painel prontinho para uso.

---

## ❓ FAQ - Dúvidas Clássicas

### 1. "Onde os meus dados estão sendo salvos?"
Tudo está armazenado dentro de um pequeno arquivo chamado `finance.db`, gerado dentro da pasta `backend`. Como usamos o **SQLite**, esse arquivo único carrega toda a estrutura de tabelas. Quer fazer um backup de toda a sua vida financeira? Basta copiar o arquivo `finance.db` para um pen-drive.

### 2. "A aplicação parou de mostrar as informações e dá erro de conexão (Failed to fetch). O que houve?"
Você provavalmente fechou a janela preta do terminal onde o `python app.py` estava rodando. Como o painel (Frontend) é apenas a "cara", ele precisa que o "cérebro" (Backend) esteja ligado para fornecer os dados. Certifique-se de que o servidor Flask está rodando.

### 3. "Como funcionam as metas financeiras e parcelamentos que citamos?"
Nós criamos a fundação de **Banco de Dados** para suportar tudo isso (ex: a tabela `transactions` tem colunas `installment_number` e `parent_transaction_id`). Porém, como focamos as rotas e o visual no Dashboard Principal (Visão Geral), nós ainda precisaríamos criar botões e modais (telas) no HTML para de fato enviar ao backend "Comprei algo em 12x", para que o backend gere as 12 transações automaticamente.

### 4. "O que o botão Sincronizar (API) faz?"
Se você tiver um ativo na sua tabela de Investimentos com o símbolo oficial, como `PETR4.SA` (Petrobras) ou `BTC-USD` (Bitcoin), ao apertar este botão o sistema vai ignorar o preço que você pagou, vai até o mercado financeiro real na internet (usando a biblioteca yfinance) e vai atualizar o preço atual, corrigindo seu patrimônio total com base na oscilação do mercado!

### 5. "Como a biblioteca Pandas ajuda na performance?"
Em vez de fazermos centenas de pequenos laços de repetição (loops "for") para calcular taxas (como a regra 50/30/20) e crescimentos mês-a-mês correndo o risco de o sistema ficar lento, nós transferimos a matemática financeira pesada para os DataFrames do Pandas, que são escritos em linguagem C por trás dos panos. Eles rodam milhares de cálculos em uma fração de segundo e só entregam a porcentagem mastigada para o gráfico do Frontend.
