#!/usr/bin/env python
import os
import sys
import re

# Configurar el directorio de trabajo
base_dir = r"d:\EQ-456\Escritorio\GISME\_AppComplementos\views"
modules = ['views_Criticidad', 'views_Producto', 'views_TipoEquipo', 'views_Tecnologia']

def analyze_view_files():
    analysis = {}
    
    for module in modules:
        analysis[module] = {
            'Commands': {},
            'Queries': {}
        }
        
        module_path = os.path.join(base_dir, module)
        if not os.path.exists(module_path):
            continue
            
        # Analizar Commands
        commands_path = os.path.join(module_path, 'Commands')
        if os.path.exists(commands_path):
            for command_dir in os.listdir(commands_path):
                command_path = os.path.join(commands_path, command_dir)
                if os.path.isdir(command_path):
                    py_files = [f for f in os.listdir(command_path) if f.endswith('.py') and f != '__init__.py']
                    for py_file in py_files:
                        analyze_file(os.path.join(command_path, py_file), analysis[module]['Commands'], command_dir)
        
        # Analizar Queries
        queries_path = os.path.join(module_path, 'Queries')
        if os.path.exists(queries_path):
            for query_dir in os.listdir(queries_path):
                query_path = os.path.join(queries_path, query_dir)
                if os.path.isdir(query_path):
                    py_files = [f for f in os.listdir(query_path) if f.endswith('.py') and f != '__init__.py']
                    for py_file in py_files:
                        analyze_file(os.path.join(query_path, py_file), analysis[module]['Queries'], query_dir)
    
    return analysis

def analyze_file(file_path, analysis_dict, category):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Buscar imports de views_base
        views_base_imports = re.findall(r'from repoGenerico\.views_base import (.+)', content)
        
        # Buscar clases que extienden APIView directamente
        direct_apiview = bool(re.search(r'class .+\(APIView\):', content))
        
        # Buscar uso de @api_view (FBV)
        fbv_usage = bool(re.search(r'@api_view', content))
        
        # Buscar definiciones de métodos HTTP
        http_methods = []
        for method in ['get', 'post', 'put', 'delete']:
            if re.search(f'def {method}\(', content):
                http_methods.append(method)
        
        # Contar líneas de código (excluyendo líneas vacías y comentarios)
        lines = [line.strip() for line in content.split('\n')]
        code_lines = [line for line in lines if line and not line.startswith('#')]
        
        analysis_dict[category] = {
            'file_path': file_path,
            'uses_views_base': bool(views_base_imports),
            'views_base_imports': views_base_imports,
            'direct_apiview': direct_apiview,
            'fbv_usage': fbv_usage,
            'http_methods': http_methods,
            'lines_of_code': len(code_lines),
            'needs_refactoring': determine_refactoring_need(views_base_imports, direct_apiview, fbv_usage, len(code_lines))
        }
        
    except Exception as e:
        analysis_dict[category] = {'error': str(e)}

def determine_refactoring_need(views_base_imports, direct_apiview, fbv_usage, lines_of_code):
    """Determina si una vista necesita refactorización"""
    # Si usa FBV, definitivamente necesita refactorización
    if fbv_usage:
        return "CRITICAL - Usando FBV (@api_view)"
    
    # Si usa APIView directamente y no importa views_base, necesita refactorización
    if direct_apiview and not views_base_imports:
        return "HIGH - APIView directo sin views_base"
    
    # Si tiene muchas líneas de código y no usa views_base, probablemente necesita refactorización
    if lines_of_code > 30 and not views_base_imports:
        return "MEDIUM - Mucho código sin views_base"
    
    # Si ya usa views_base, está bien
    if views_base_imports:
        return "OK - Usando views_base"
    
    return "LOW - Revisar"

def print_analysis(analysis):
    print("🔍 ANÁLISIS DE VISTAS CBV/DRF EN MÓDULOS DE COMPLEMENTOS")
    print("=" * 80)
    
    for module, categories in analysis.items():
        print(f"\n📦 {module}")
        print("-" * 40)
        
        for category_type, items in categories.items():
            if items:
                print(f"\n  📂 {category_type}:")
                for item_name, item_data in items.items():
                    if 'error' in item_data:
                        print(f"    ❌ {item_name}: ERROR - {item_data['error']}")
                        continue
                        
                    status_icon = "✅" if item_data['needs_refactoring'] == "OK - Usando views_base" else "⚠️" if "MEDIUM" in item_data['needs_refactoring'] else "🚨" if "HIGH" in item_data['needs_refactoring'] or "CRITICAL" in item_data['needs_refactoring'] else "🔍"
                    
                    print(f"    {status_icon} {item_name}")
                    print(f"       • Estado: {item_data['needs_refactoring']}")
                    print(f"       • Líneas de código: {item_data['lines_of_code']}")
                    print(f"       • Métodos HTTP: {', '.join(item_data['http_methods'])}")
                    if item_data['views_base_imports']:
                        print(f"       • Imports views_base: {', '.join(item_data['views_base_imports'])}")

if __name__ == "__main__":
    analysis = analyze_view_files()
    print_analysis(analysis)
