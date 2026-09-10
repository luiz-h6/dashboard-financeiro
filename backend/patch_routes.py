import os
import re

routes_dir = r"c:\Users\luiz_\Desktop\dashboard financeiro\backend\routes"
files_to_modify = [
    "account_routes.py",
    "analytics_routes.py",
    "budget_routes.py",
    "category_routes.py",
    "investment_routes.py",
    "transaction_routes.py"
]

for filename in files_to_modify:
    filepath = os.path.join(routes_dir, filename)
    if not os.path.exists(filepath):
        continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Adicionar o import do token_required no topo
    if "from middleware.auth import token_required" not in content:
        content = "from middleware.auth import token_required\n" + content
        
    # Remover get_current_user_id function definition e commentários relacionados
    content = re.sub(r'# Simulando um middleware de auth:.*?def get_current_user_id\(\):\s*return request\.headers\.get\(\'X-User-Id\', 1\)', '', content, flags=re.DOTALL)
    content = re.sub(r'def get_current_user_id\(\):\s*return request\.headers\.get\(\'X-User-Id\', 1\)', '', content)
    
    # Regex para adicionar @token_required e injetar current_user_id
    # Procurar por @bp.route e def <name>(<args>):
    
    def replacer(match):
        route_decorator = match.group(1)
        func_def = match.group(2)
        func_name = match.group(3)
        args_str = match.group(4)
        body = match.group(5)
        
        # Add current_user_id to arguments
        if args_str.strip() == '':
            new_args = 'current_user_id'
        else:
            new_args = 'current_user_id, ' + args_str
            
        # Replace occurrences of get_current_user_id() with current_user_id
        new_body = re.sub(r'get_current_user_id\(\)', 'current_user_id', body)
        
        return f"{route_decorator}\n@token_required\n{func_def}{func_name}({new_args}):{new_body}"

    pattern = re.compile(r'(@bp\.route.*?)\n(def\s+)([a-zA-Z0-9_]+)\((.*?)\):(.*?)(?=\n@bp\.route|\Z)', re.DOTALL)
    
    content = pattern.sub(replacer, content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Patch concluded.")
