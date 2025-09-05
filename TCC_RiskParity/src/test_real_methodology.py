"""
TESTE DA METODOLOGIA COM DADOS REAIS DA ECONOMATICA
==================================================

Teste rápido para validar se a nova metodologia funciona com dados 100% reais.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from final_methodology import FinalMethodologyAnalyzer

def main():
    """
    Teste da metodologia reconstruída com dados reais
    """
    print("=== TESTE METODOLOGIA COM DADOS REAIS DA ECONOMATICA ===")
    print("Objetivo: Validar carregamento e processamento dos dados")
    print()
    
    # Instanciar analisador
    analyzer = FinalMethodologyAnalyzer()
    
    try:
        # Teste 1: Carregamento dos dados
        print("TESTE 1: Carregamento dos dados...")
        success = analyzer.load_extended_data()
        
        if not success:
            print("[ERRO] FALHA: Nao conseguiu carregar dados reais")
            return False
        
        print("[OK] SUCESSO: Dados reais carregados da Economatica")
        print()
        
        # Teste 2: Configuração dos períodos
        print("TESTE 2: Configuracao dos periodos de rebalanceamento...")
        analyzer.setup_rebalancing_periods()
        print(f"[OK] SUCESSO: {len(analyzer.estimation_periods)} periodos configurados")
        print()
        
        # Teste 3: Estimação de parâmetros (primeiro período)
        print("TESTE 3: Estimacao de parametros (primeiro periodo)...")
        if len(analyzer.estimation_periods) > 0:
            first_period = analyzer.estimation_periods[0]
            
            est_data = analyzer.full_returns[
                (analyzer.full_returns.index >= first_period['estimation_start']) &
                (analyzer.full_returns.index <= first_period['estimation_end'])
            ]
            
            if len(est_data) > 0:
                parameters = analyzer.estimate_parameters(est_data)
                print(f"[OK] SUCESSO: Parametros estimados com {parameters['n_observations']} observacoes")
                print(f"  Retornos anualizados medios: {parameters['expected_returns'].mean():.2%}")
                print(f"  Volatilidade media: {parameters['volatilities'].mean():.2%}")
                print()
                
                # Teste 4: Otimização das estratégias
                print("TESTE 4: Otimizacao das estrategias...")
                
                # Equal Weight
                ew_weights = analyzer.equal_weight_strategy(est_data.columns)
                print(f"  Equal Weight: [OK] {len(ew_weights)} ativos, soma = {ew_weights.sum():.3f}")
                
                # Markowitz
                markowitz_weights = analyzer.markowitz_optimization(parameters)
                print(f"  Markowitz: [OK] {len(markowitz_weights)} ativos, soma = {markowitz_weights.sum():.3f}")
                
                # Risk Parity
                rp_weights = analyzer.risk_parity_strategy(parameters)
                print(f"  Risk Parity: [OK] {len(rp_weights)} ativos, soma = {rp_weights.sum():.3f}")
                
                print()
                print("RESUMO DOS TESTES:")
                print("[OK] Dados reais da Economatica carregados")
                print("[OK] Periodos de rebalanceamento configurados") 
                print("[OK] Parametros estatisticos estimados")
                print("[OK] Todas as 3 estrategias funcionando")
                print()
                print("PRONTO PARA EXECUTAR METODOLOGIA COMPLETA!")
                
                return True
            else:
                print("[ERRO] FALHA: Dados de estimacao insuficientes")
                return False
        else:
            print("[ERRO] FALHA: Nenhum periodo de estimacao configurado")
            return False
            
    except Exception as e:
        print(f"[ERRO] durante teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n" + "="*60)
        print("PROXIMO PASSO: Executar methodology completa")
        print("Comando: python final_methodology.py")
        print("="*60)
    else:
        print("\n[ERRO] NECESSARIO CORRIGIR ERROS ANTES DE PROSSEGUIR")