"""
TESTE DA METODOLOGIA CORRIGIDA
==============================

Testa a metodologia com out-of-sample rigoroso corrigido.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from final_methodology import FinalMethodologyAnalyzer

def test_corrected_periods():
    """
    Testa se os períodos estão corretos após a correção
    """
    print("="*80)
    print("TESTE DA METODOLOGIA OUT-OF-SAMPLE CORRIGIDA")
    print("="*80)
    
    analyzer = FinalMethodologyAnalyzer()
    
    # Carregar dados
    print("\n1. CARREGANDO DADOS...")
    success = analyzer.load_extended_data()
    
    if not success:
        print("ERRO: Não conseguiu carregar dados")
        return False
    
    # Configurar períodos
    print("\n2. CONFIGURANDO PERIODOS...")
    analyzer.setup_rebalancing_periods()
    
    # Verificar se os períodos estão corretos
    print("\n3. VERIFICANDO RIGOR OUT-OF-SAMPLE...")
    
    all_valid = True
    
    for i, period in enumerate(analyzer.estimation_periods):
        print(f"\nSEMESTRE {i+1}:")
        print(f"  Estimacao: {period['estimation_start'].date()} a {period['estimation_end'].date()}")
        print(f"  Teste: {period['testing_start'].date()} a {period['testing_end'].date()}")
        
        # Verificar gap temporal
        gap_days = (period['testing_start'] - period['estimation_end']).days
        print(f"  Gap temporal: {gap_days} dias")
        
        # Validar
        gap_valid = gap_days > 0
        print(f"  Status: {'[OK]' if gap_valid else '[ERRO] SOBREPOSICAO'}")
        
        all_valid = all_valid and gap_valid
        
        # Verificar dados disponíveis
        est_data = analyzer.full_returns[
            (analyzer.full_returns.index >= period['estimation_start']) &
            (analyzer.full_returns.index <= period['estimation_end'])
        ]
        
        test_data = analyzer.full_returns[
            (analyzer.full_returns.index >= period['testing_start']) &
            (analyzer.full_returns.index <= period['testing_end'])
        ]
        
        print(f"  Dados estimacao: {len(est_data)} meses")
        print(f"  Dados teste: {len(test_data)} meses")
        
        # Verificar suficiência
        data_valid = len(est_data) >= 20 and len(test_data) >= 3
        print(f"  Dados suficientes: {'[OK]' if data_valid else '[ERRO]'}")
        
        all_valid = all_valid and data_valid
    
    print(f"\n4. RESULTADO FINAL:")
    print(f"   RIGOR OUT-OF-SAMPLE: {'[OK] CORRIGIDO' if all_valid else '[ERRO] AINDA COM PROBLEMAS'}")
    
    return all_valid

def test_quick_execution():
    """
    Teste rápido de execução da metodologia corrigida
    """
    print(f"\n5. TESTE RAPIDO DE EXECUCAO...")
    
    analyzer = FinalMethodologyAnalyzer()
    
    try:
        # Carregar e configurar
        analyzer.load_extended_data()
        analyzer.setup_rebalancing_periods()
        
        # Testar primeiro período apenas
        if len(analyzer.estimation_periods) > 0:
            first_period = analyzer.estimation_periods[0]
            
            est_data = analyzer.full_returns[
                (analyzer.full_returns.index >= first_period['estimation_start']) &
                (analyzer.full_returns.index <= first_period['estimation_end'])
            ]
            
            test_data = analyzer.full_returns[
                (analyzer.full_returns.index >= first_period['testing_start']) &
                (analyzer.full_returns.index <= first_period['testing_end'])
            ]
            
            print(f"   Testando primeiro periodo...")
            print(f"   Estimacao: {len(est_data)} meses")
            print(f"   Teste: {len(test_data)} meses")
            
            # Estimar parâmetros
            parameters = analyzer.estimate_parameters(est_data)
            print(f"   Parametros estimados: [OK]")
            
            # Testar estratégias
            markowitz_weights = analyzer.markowitz_optimization(parameters)
            ew_weights = analyzer.equal_weight_strategy(est_data.columns)
            rp_weights = analyzer.risk_parity_strategy(parameters)
            
            print(f"   Markowitz: {markowitz_weights.sum():.3f} (soma)")
            print(f"   Equal Weight: {ew_weights.sum():.3f} (soma)")
            print(f"   Risk Parity: {rp_weights.sum():.3f} (soma)")
            
            # Calcular métricas
            metrics_mark = analyzer.calculate_portfolio_metrics(markowitz_weights, test_data, "Teste")
            
            print(f"   Metricas calculadas: [OK]")
            print(f"   Sharpe Markowitz: {metrics_mark['sharpe_ratio']:.3f}")
            
            return True
            
    except Exception as e:
        print(f"   [ERRO] Falha no teste: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return False

def main():
    """
    Executa todos os testes da metodologia corrigida
    """
    periods_valid = test_corrected_periods()
    execution_valid = test_quick_execution()
    
    print(f"\n" + "="*80)
    print("RESUMO DOS TESTES")
    print("="*80)
    print(f"Periodos corrigidos: {'[OK]' if periods_valid else '[ERRO]'}")
    print(f"Execucao funcional: {'[OK]' if execution_valid else '[ERRO]'}")
    
    overall_success = periods_valid and execution_valid
    print(f"\nMETODOLOGIA CORRIGIDA: {'[OK] PRONTA PARA USO' if overall_success else '[ERRO] REQUER MAIS CORRECOES'}")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    
    if success:
        print(f"\n🎯 METODOLOGIA VALIDADA! Pode prosseguir com execucao completa.")
    else:
        print(f"\n⚠️  METODOLOGIA AINDA REQUER CORRECOES!")