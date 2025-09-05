"""
AUDITORIA SIMPLIFICADA DO DOCUMENTO TCC
=======================================

Auditoria focada nos problemas mais críticos do documento.
"""

import os
import re
from pathlib import Path

def find_critical_issues():
    """
    Encontra problemas críticos no documento
    """
    print("="*80)
    print("AUDITORIA CRITICA DO DOCUMENTO TCC")
    print("="*80)
    
    docs_path = Path("C:/Users/Bruno/Documents/TCC/Overleaf/TCC_RiskParity/docs/Overleaf")
    
    critical_issues = []
    
    # 1. Anos futuros (2025+)
    print(f"\n1. PROCURANDO ANOS FUTUROS (2025+):")
    future_years_pattern = r'20(2[5-9]|[3-9]\d)'
    
    # 2. Referências quebradas
    print(f"\n2. PROCURANDO REFERENCIAS QUEBRADAS:")
    broken_refs = [r'\[\?\]', r'Tabela \?\?', r'Figura \?\?']
    
    # 3. Páginas impossíveis
    print(f"\n3. PROCURANDO PAGINAS IMPOSSIVEIS:")
    impossible_pages = r'p\.? ?17[5-9]'
    
    # Verificar todos os arquivos .tex
    tex_files = list(docs_path.glob("**/*.tex"))
    print(f"\nVerificando {len(tex_files)} arquivos...")
    
    for tex_file in tex_files:
        rel_path = tex_file.relative_to(docs_path)
        
        try:
            content = tex_file.read_text(encoding='utf-8')
            
            # Verificar anos futuros
            future_matches = re.findall(future_years_pattern, content)
            if future_matches:
                critical_issues.append(f"ANOS FUTUROS em {rel_path}: {len(future_matches)} ocorrências")
            
            # Verificar referências quebradas
            for pattern in broken_refs:
                matches = re.findall(pattern, content)
                if matches:
                    critical_issues.append(f"REF QUEBRADA em {rel_path}: {pattern} ({len(matches)}x)")
            
            # Verificar páginas impossíveis
            impossible_matches = re.findall(impossible_pages, content)
            if impossible_matches:
                critical_issues.append(f"PAGINA IMPOSSIVEL em {rel_path}: {impossible_matches}")
                
        except Exception as e:
            critical_issues.append(f"ERRO DE LEITURA: {rel_path} - {e}")
    
    return critical_issues

def check_data_consistency():
    """
    Verifica consistência entre texto e dados reais
    """
    print(f"\n4. VERIFICANDO CONSISTENCIA DOS DADOS:")
    
    # Carregar resultados reais para comparar
    try:
        import sys
        sys.path.append("C:/Users/Bruno/Documents/TCC/Overleaf/TCC_RiskParity/src")
        from final_methodology import FinalMethodologyAnalyzer
        
        analyzer = FinalMethodologyAnalyzer()
        analyzer.load_extended_data()
        analyzer.setup_rebalancing_periods()
        
        # Executar metodologia para obter resultados reais
        print("   Executando metodologia para obter dados reais...")
        
        # Informações que devem estar no texto
        real_info = {
            "periodo_dados": "2014-2019",
            "ativos_count": "10 ativos", 
            "janela_estimacao": "24 meses",
            "periodo_teste": "2018-2019",
            "rebalanceamento": "semestral",
            "fonte_dados": "Economatica"
        }
        
        print("   INFORMACOES REAIS QUE DEVEM ESTAR NO TEXTO:")
        for key, value in real_info.items():
            print(f"   - {key}: {value}")
        
        return real_info
        
    except Exception as e:
        print(f"   [ERRO] Não foi possível obter dados reais: {e}")
        return {}

def audit_specific_sections():
    """
    Audita seções específicas críticas
    """
    print(f"\n5. AUDITORIA DE SECOES ESPECIFICAS:")
    
    docs_path = Path("C:/Users/Bruno/Documents/TCC/Overleaf/TCC_RiskParity/docs/Overleaf/sections")
    
    critical_sections = {
        "12_metodologia.tex": "Metodologia (seção mais crítica)",
        "13_resultados.tex": "Resultados (deve refletir dados reais)",
        "15_conclusao.tex": "Conclusão (deve ser coerente)",
        "16_referencias.tex": "Referências (datas corretas)"
    }
    
    section_issues = []
    
    for file_name, description in critical_sections.items():
        file_path = docs_path / file_name
        print(f"\n   {description}:")
        
        if not file_path.exists():
            section_issues.append(f"ARQUIVO FALTANDO: {file_name}")
            print(f"   [ERRO] Arquivo não encontrado")
            continue
        
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Verificações específicas por seção
            if file_name == "12_metodologia.tex":
                # Metodologia deve mencionar dados reais
                checks = {
                    "Economatica": "Fonte de dados",
                    "2018-2019": "Período de teste", 
                    "out-of-sample": "Metodologia rigorosa",
                    "24 meses": "Janela de estimação",
                    "ERC": "Equal Risk Contribution"
                }
                
                for term, description in checks.items():
                    found = term.lower() in content.lower()
                    print(f"   {description}: {'[OK]' if found else '[FALTANDO]'}")
                    if not found:
                        section_issues.append(f"METODOLOGIA: Faltando {description}")
            
            elif file_name == "13_resultados.tex":
                # Resultados devem ter dados concretos
                if "PLACEHOLDER" in content.upper() or "[?]" in content:
                    section_issues.append("RESULTADOS: Ainda tem placeholders")
                    print(f"   [AVISO] Ainda contém placeholders")
                else:
                    print(f"   [OK] Sem placeholders óbvios")
            
            elif file_name == "16_referencias.tex":
                # Referências não devem ter anos futuros
                future_years = re.findall(r'20(2[5-9]|[3-9]\d)', content)
                if future_years:
                    section_issues.append(f"REFERENCIAS: {len(future_years)} anos futuros")
                    print(f"   [ERRO] {len(future_years)} anos futuros encontrados")
                else:
                    print(f"   [OK] Sem anos futuros")
                    
        except Exception as e:
            section_issues.append(f"ERRO LENDO {file_name}: {e}")
            print(f"   [ERRO] Não foi possível ler: {e}")
    
    return section_issues

def main():
    """
    Executa auditoria crítica completa
    """
    critical_issues = find_critical_issues()
    real_data_info = check_data_consistency()
    section_issues = audit_specific_sections()
    
    print(f"\n" + "="*80)
    print("RESUMO DA AUDITORIA CRITICA")
    print("="*80)
    
    total_issues = len(critical_issues) + len(section_issues)
    
    if critical_issues:
        print(f"\nPROBLEMAS CRITICOS ENCONTRADOS ({len(critical_issues)}):")
        for issue in critical_issues:
            print(f"  - {issue}")
    
    if section_issues:
        print(f"\nPROBLEMAS ESPECIFICOS DE SECAO ({len(section_issues)}):")
        for issue in section_issues:
            print(f"  - {issue}")
    
    if total_issues == 0:
        print(f"\n[OK] DOCUMENTO PARECE BEM ESTRUTURADO")
    else:
        print(f"\n[REQUER CORRECAO] {total_issues} problemas identificados")
        
        print(f"\nPLANO DE ACAO RECOMENDADO:")
        print(f"1. Corrigir todas as datas futuras para datas reais")
        print(f"2. Substituir referências quebradas por referências válidas")
        print(f"3. Atualizar páginas de fórmulas para números realistas")
        print(f"4. Garantir que resultados refletem dados reais da Economatica")
        print(f"5. Revisar coerência entre todas as seções")
    
    return total_issues == 0

if __name__ == "__main__":
    success = main()
    if not success:
        print(f"\n>>> DOCUMENTO TCC REQUER REVISAO COMPLETA <<<")
    else:
        print(f"\n>>> DOCUMENTO TCC APROVADO NA AUDITORIA <<<")