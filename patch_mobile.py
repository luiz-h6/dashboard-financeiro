import os
import re

index_path = r"c:\Users\luiz_\Desktop\dashboard financeiro\frontend\index.html"

with open(index_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Esconder o texto do usuário no mobile para economizar espaço
content = content.replace('<span id="topUserName" class="text-sm text-slate-300 font-medium">', '<span id="topUserName" class="text-sm text-slate-300 font-medium hidden sm:block">')
content = content.replace('class="flex items-center space-x-3 bg-navy-800 border border-slate-700 px-3 py-1.5 rounded-full"', 'class="flex items-center space-x-2 sm:space-x-3 bg-navy-800 border border-slate-700 px-2 sm:px-3 py-1.5 rounded-full"')

# 2. Adicionar margem inferior ao main no mobile (pb-20)
content = content.replace('<main class="flex-1 overflow-y-auto bg-navy-900 relative">', '<main class="flex-1 overflow-y-auto bg-navy-900 relative pb-20 md:pb-0">')

# 3. Adicionar o Bottom Menu Bar logo antes de fechar o <main>
bottom_nav = """
            <!-- Bottom Nav (Mobile) -->
            <nav class="md:hidden fixed bottom-0 left-0 w-full bg-navy-800 border-t border-slate-700 flex justify-around p-3 z-50">
                <button onclick="switchTab('dashboard')" class="text-slate-400 hover:text-neon-cyan flex flex-col items-center">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"></path></svg>
                    <span class="text-[10px] mt-1 font-medium">Painel</span>
                </button>
                <button onclick="switchTab('lancamentos')" class="text-slate-400 hover:text-neon-cyan flex flex-col items-center">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
                    <span class="text-[10px] mt-1 font-medium">Lançar</span>
                </button>
                <button onclick="switchTab('historico')" class="text-slate-400 hover:text-neon-cyan flex flex-col items-center">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path></svg>
                    <span class="text-[10px] mt-1 font-medium">Histórico</span>
                </button>
                <button onclick="switchTab('evolucao')" class="text-slate-400 hover:text-neon-cyan flex flex-col items-center">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z"></path></svg>
                    <span class="text-[10px] mt-1 font-medium">Evolução</span>
                </button>
                <button onclick="switchTab('budgets')" class="text-slate-400 hover:text-neon-cyan flex flex-col items-center">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
                    <span class="text-[10px] mt-1 font-medium">Metas</span>
                </button>
            </nav>
"""

content = content.replace('</main>', bottom_nav + '\n        </main>')

with open(index_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Mobile UI patched.")
