"""
AUDITORIA COMPLETA DO DOCUMENTO TCC
===================================

Audita TODOS os aspectos do documento LaTeX para garantir consistência e correção.
"""

import os
import re
from datetime import datetime
import pandas as pd

def audit_file_structure():
    """
    Audita a estrutura de arquivos do TCC
    """
    print("="*80)
    print("AUDITORIA COMPLETA DO DOCUMENTO TCC")
    print("="*80)
    
    base_path = "C:\\Users\\Bruno\\Documents\\TCC\\Overleaf\\TCC_RiskParity"
    docs_path = os.path.join(base_path, "docs", "Overleaf")
    
    print(f"\n1. ESTRUTURA DE ARQUIVOS:")
    print(f"   Base: {base_path}")
    print(f"   Docs: {docs_path}")
    
    # Verificar arquivos principais
    main_files = {
        "main.tex": "Documento principal",
        "sections/01_capa.tex": "Capa",
        "sections/10_introducao.tex": "Introdução", 
        "sections/11_referencial_teorico.tex": "Referencial Teórico",
        "sections/12_metodologia.tex": "Metodologia",
        "sections/13_resultados.tex": "Resultados",
        "sections/15_conclusao.tex": "Conclusão",
        "sections/16_referencias.tex": "Referências"
    }
    
    print(f"\n   ARQUIVOS PRINCIPAIS:")
    missing_files = []
    for file_path, description in main_files.items():
        full_path = os.path.join(docs_path, file_path)
        exists = os.path.exists(full_path)
        print(f"   {description}: {'[OK]' if exists else '[FALTANDO]'}")
        if not exists:
            missing_files.append(file_path)
    
    # Verificar diretórios de apoio
    support_dirs = ["tables", "figures", "images"]
    print(f"\n   DIRETORIOS DE APOIO:")
    for dir_name in support_dirs:
        dir_path = os.path.join(docs_path, dir_name)
        exists = os.path.exists(dir_path)
        if exists:
            files_count = len([f for f in os.listdir(dir_path) if f.endswith(('.tex', '.pdf', '.png', '.jpg'))])
            print(f"   {dir_name}/: [OK] ({files_count} arquivos)")
        else:
            print(f"   {dir_name}/: [FALTANDO]")
    
    return len(missing_files) == 0

def audit_main_document():
    """
    Audita o documento principal main.tex
    """
    print(f"\n2. DOCUMENTO PRINCIPAL (main.tex):")
    
    main_path = "C:\\Users\\Bruno\\Documents\\TCC\\Overleaf\\TCC_RiskParity\\docs\\Overleaf\\main.tex"
    
    if not os.path.exists(main_path):
        print(f"   [ERRO] main.tex não encontrado")
        return False
    
    with open(main_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar estrutura básica
    checks = {
        "\\documentclass": "Classe do documento",
        "\\usepackage": "Pacotes importados", 
        "\\begin{document}": "Início do documento",
        "\\end{document}": "Fim do documento",
        "\\input{sections/10_introducao}": "Inclusão da introdução",
        "\\input{sections/12_metodologia}": "Inclusão da metodologia",
        "\\input{sections/13_resultados}": "Inclusão dos resultados"
    }
    
    print(f"   ESTRUTURA BASICA:")
    all_good = True
    for pattern, description in checks.items():
        found = pattern in content
        print(f"   {description}: {'[OK]' if found else '[FALTANDO]'}")
        all_good = all_good and found
    
    # Verificar encoding
    print(f"\n   ENCODING:")
    try:
        with open(main_path, 'r', encoding='utf-8') as f:
            f.read()
        print(f"   UTF-8: [OK]")
    except UnicodeDecodeError:
        print(f"   UTF-8: [ERRO] Problema de encoding")
        all_good = False
    
    return all_good

def audit_dates_and_references():
    """
    Audita datas e referências em todo o documento
    """
    print(f"\n3. DATAS E REFERENCIAS:")
    
    docs_path = "C:\\Users\\Bruno\\Documents\\TCC\\Overleaf\\TCC_RiskParity\\docs\\Overleaf"
    
    # Padrões problemáticos
    problematic_patterns = {
        r'20(2[5-9]|[3-9]\d)': "Anos futuros (2025+)",
        r'\[\\?\?\]': "Placeholders de referência",
        r'Tabela \\?\?': "Referências de tabela quebradas",
        r'Figura \\?\?': "Referências de figura quebradas", 
        r'Equação \\?\?': "Referências de equação quebradas",
        r'p\\.? ?175-177': "Páginas impossíveis de fórmulas",
        r'Investidor10': "Fonte questionável CDI"
    }
    
    issues_found = {}
    
    # Verificar arquivos .tex
    tex_files = []
    for root, dirs, files in os.walk(docs_path):
        for file in files:
            if file.endswith('.tex'):
                tex_files.append(os.path.join(root, file))
    
    print(f"   Verificando {len(tex_files)} arquivos .tex...")
    
    for tex_file in tex_files:
        file_name = os.path.basename(tex_file)
        
        try:
            with open(tex_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_issues = []
            for pattern, description in problematic_patterns.items():
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    file_issues.append(f"{description}: {len(matches)} ocorrências")
            
            if file_issues:
                issues_found[file_name] = file_issues
                
        except Exception as e:
            print(f"   [ERRO] Não foi possível ler {file_name}: {e}")
    
    # Reportar problemas encontrados
    if issues_found:
        print(f"\n   PROBLEMAS ENCONTRADOS:")
        for file_name, issues in issues_found.items():
            print(f"   {file_name}:")
            for issue in issues:
                print(f"     - {issue}")
    else:
        print(f"   [OK] Nenhum problema de data/referência encontrado")
    
    return len(issues_found) == 0

def audit_mathematical_content():
    """
    Audita conteúdo matemático e fórmulas
    """
    print(f"\n4. CONTEUDO MATEMATICO:")
    
    metodologia_path = "C:\\Users\\Bruno\\Documents\\TCC\\Overleaf\\TCC_RiskParity\\docs\\Overleaf\\sections\\12_metodologia.tex"
    
    if not os.path.exists(metodologia_path):
        print(f"   [ERRO] Arquivo de metodologia não encontrado")
        return False
    
    with open(metodologia_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar fórmulas essenciais
    essential_formulas = {
        r'\\log\\(': "Retornos logarítmicos", 
        r'Sharpe': "Fórmula Sharpe Ratio",
        r'\\sigma_p': "Volatilidade do portfólio",
        r'ERC|Equal.Risk.Contribution': "Equal Risk Contribution",
        r'Markowitz': "Otimização de Markowitz",
        r'\\min\\s|minimize': "Função objetivo de minimização"
    }
    
    print(f"   FORMULAS ESSENCIAIS:")
    formulas_ok = True
    for pattern, description in essential_formulas.items():
        found = bool(re.search(pattern, content, re.IGNORECASE))
        print(f"   {description}: {'[OK]' if found else '[FALTANDO]'}")
        if not found:
            formulas_ok = False
    
    # Verificar consistência de notação
    print(f"\n   NOTACAO MATEMATICA:")
    notations = {
        r'R_p|r_p': "Retorno do portfólio",
        r'\\sigma|\\\\sigma': "Símbolo de volatilidade", 
        r'w_i|w_j': "Pesos dos ativos",
        r'\\Sigma|\\\\Sigma': "Matriz de covariância"
    }
    
    for pattern, description in notations.items():
        found = bool(re.search(pattern, content, re.IGNORECASE))
        print(f"   {description}: {'[OK]' if found else '[AVISO] Pouco usado'}")
    
    return formulas_ok

def audit_table_figure_references():
    """
    Audita referências a tabelas e figuras
    """
    print(f"\n5. TABELAS E FIGURAS:")
    
    docs_path = "C:\\Users\\Bruno\\Documents\\TCC\\Overleaf\\TCC_RiskParity\\docs\\Overleaf"
    
    # Procurar arquivos de tabela
    tables_dir = os.path.join(docs_path, "tables")
    figures_dir = os.path.join(docs_path, "figures")
    
    table_files = []
    if os.path.exists(tables_dir):
        table_files = [f for f in os.listdir(tables_dir) if f.endswith('.tex')]
    
    figure_files = []
    if os.path.exists(figures_dir):
        figure_files = [f for f in os.listdir(figures_dir) if f.endswith(('.png', '.pdf', '.jpg'))]
    
    print(f"   INVENTARIO:")
    print(f"   Tabelas: {len(table_files)} arquivos")
    for table in table_files:
        print(f"     - {table}")
    
    print(f"   Figuras: {len(figure_files)} arquivos") 
    for figure in figure_files:
        print(f"     - {figure}")
    
    # Verificar referências no texto principal
    main_sections = ["13_resultados.tex", "12_metodologia.tex", "11_referencial_teorico.tex"]
    
    print(f"\n   VERIFICACAO DE REFERENCIAS:")
    
    for section in main_sections:
        section_path = os.path.join(docs_path, "sections", section)
        if os.path.exists(section_path):
            with open(section_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Contar referências
            table_refs = len(re.findall(r'\\ref\\{tab:', content))
            figure_refs = len(re.findall(r'\\ref\\{fig:', content))
            
            print(f"   {section}: {table_refs} refs tabelas, {figure_refs} refs figuras")
    
    return True

def main():
    """
    Executa auditoria completa do documento
    """
    structure_ok = audit_file_structure()
    main_doc_ok = audit_main_document() 
    dates_ok = audit_dates_and_references()
    math_ok = audit_mathematical_content()
    refs_ok = audit_table_figure_references()
    
    print(f"\n" + "="*80)
    print("RESUMO DA AUDITORIA DOCUMENTAL")
    print("="*80)
    print(f"Estrutura de arquivos: {'[OK]' if structure_ok else '[PROBLEMAS]'}")
    print(f"Documento principal: {'[OK]' if main_doc_ok else '[PROBLEMAS]'}")
    print(f"Datas e referências: {'[OK]' if dates_ok else '[PROBLEMAS]'}")
    print(f"Conteúdo matemático: {'[OK]' if math_ok else '[PROBLEMAS]'}")
    print(f"Tabelas e figuras: {'[OK]' if refs_ok else '[PROBLEMAS]'}")
    
    overall_ok = all([structure_ok, main_doc_ok, dates_ok, math_ok, refs_ok])
    print(f"\nDOCUMENTO TCC: {'[OK] BEM ESTRUTURADO' if overall_ok else '[REQUER REVISAO COMPLETA]'}")
    
    if not overall_ok:
        print(f"\nPROXIMOS PASSOS:")
        print(f"1. Corrigir problemas identificados")
        print(f"2. Atualizar conteúdo com dados reais")
        print(f"3. Verificar coerência texto-resultados")
        print(f"4. Revisar conclusões")
    
    return overall_ok

if __name__ == "__main__":
    main()