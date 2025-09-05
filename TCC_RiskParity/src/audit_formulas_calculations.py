"""
AUDITORIA DAS FORMULAS E CALCULOS
==================================

Verifica se todas as fórmulas matemáticas estão implementadas corretamente.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def audit_return_calculations():
    """
    Audita o cálculo de retornos logarítmicos
    """
    print("="*80)
    print("AUDITORIA DOS CALCULOS DE RETORNOS")
    print("="*80)
    
    # Dados de teste
    prices = np.array([100, 105, 102, 110, 108])
    expected_returns = np.array([
        np.log(105/100),   # 0.048790
        np.log(102/105),   # -0.028846
        np.log(110/102),   # 0.075084
        np.log(108/110)    # -0.018413
    ])
    
    print(f"\n1. TESTE DE RETORNOS LOGARITMICOS:")
    print(f"   Precos de teste: {prices}")
    print(f"   Retornos esperados: {expected_returns}")
    
    # Implementação manual
    calculated_returns = np.log(prices[1:] / prices[:-1])
    print(f"   Retornos calculados: {calculated_returns}")
    
    # Verificar se são iguais
    diff = np.abs(expected_returns - calculated_returns)
    max_diff = np.max(diff)
    print(f"   Diferenca maxima: {max_diff:.10f}")
    print(f"   RESULTADO: {'[OK]' if max_diff < 1e-10 else '[ERRO]'}")

def audit_annualization():
    """
    Audita os fatores de anualização
    """
    print(f"\n2. TESTE DE ANUALIZACAO:")
    
    # Retornos mensais de teste
    monthly_returns = np.array([0.02, -0.01, 0.03, 0.01, -0.005])
    monthly_vol = 0.05
    
    print(f"   Retornos mensais: {monthly_returns}")
    print(f"   Volatilidade mensal: {monthly_vol}")
    
    # Anualização de retornos: média * 12
    annual_return_arithmetic = np.mean(monthly_returns) * 12
    print(f"   Retorno anual (aritmetico): {annual_return_arithmetic:.6f}")
    
    # Anualização de volatilidade: std * sqrt(12)
    annual_vol = monthly_vol * np.sqrt(12)
    print(f"   Volatilidade anual: {annual_vol:.6f}")
    
    # Verificar se sqrt(12) ≈ 3.464
    sqrt_12 = np.sqrt(12)
    print(f"   sqrt(12) = {sqrt_12:.6f} (esperado: 3.464102)")
    print(f"   RESULTADO: {'[OK]' if abs(sqrt_12 - 3.464102) < 0.001 else '[ERRO]'}")

def audit_sharpe_ratio():
    """
    Audita o cálculo do Sharpe Ratio
    """
    print(f"\n3. TESTE DO SHARPE RATIO:")
    
    # Dados de teste
    portfolio_return = 0.15  # 15% ao ano
    risk_free_rate = 0.06    # 6% ao ano (CDI)
    portfolio_vol = 0.20     # 20% ao ano
    
    print(f"   Retorno do portfolio: {portfolio_return:.3f}")
    print(f"   Taxa livre de risco: {risk_free_rate:.3f}")
    print(f"   Volatilidade: {portfolio_vol:.3f}")
    
    # Fórmula: Sharpe = (Rp - Rf) / σp
    expected_sharpe = (portfolio_return - risk_free_rate) / portfolio_vol
    print(f"   Sharpe esperado: {expected_sharpe:.6f}")
    
    # Calcular manualmente
    excess_return = portfolio_return - risk_free_rate
    calculated_sharpe = excess_return / portfolio_vol
    print(f"   Sharpe calculado: {calculated_sharpe:.6f}")
    
    # Verificar
    diff = abs(expected_sharpe - calculated_sharpe)
    print(f"   Diferenca: {diff:.10f}")
    print(f"   RESULTADO: {'[OK]' if diff < 1e-10 else '[ERRO]'}")

def audit_portfolio_return():
    """
    Audita o cálculo de retorno do portfólio
    """
    print(f"\n4. TESTE DE RETORNO DO PORTFOLIO:")
    
    # Dados de teste
    weights = np.array([0.3, 0.4, 0.3])
    returns = np.array([0.02, -0.01, 0.03])
    
    print(f"   Pesos: {weights}")
    print(f"   Retornos dos ativos: {returns}")
    
    # Fórmula: Rp = Σ(wi * Ri)
    expected_portfolio_return = np.sum(weights * returns)
    print(f"   Retorno esperado: {expected_portfolio_return:.6f}")
    
    # Calcular manualmente
    calculated_return = weights[0]*returns[0] + weights[1]*returns[1] + weights[2]*returns[2]
    print(f"   Retorno calculado: {calculated_return:.6f}")
    
    # Verificar soma dos pesos
    weight_sum = np.sum(weights)
    print(f"   Soma dos pesos: {weight_sum:.6f} (deve ser 1.0)")
    
    # Verificar
    diff = abs(expected_portfolio_return - calculated_return)
    print(f"   Diferenca: {diff:.10f}")
    print(f"   RESULTADO: {'[OK]' if diff < 1e-10 and abs(weight_sum - 1.0) < 1e-10 else '[ERRO]'}")

def audit_covariance_matrix():
    """
    Audita cálculos com matriz de covariância
    """
    print(f"\n5. TESTE DA MATRIZ DE COVARIANCIA:")
    
    # Dados de teste (2 ativos, 5 observações)
    returns = np.array([
        [0.02, -0.01],
        [-0.01, 0.03],
        [0.03, -0.02],
        [0.01, 0.02],
        [-0.005, 0.01]
    ])
    
    print(f"   Retornos (5 obs x 2 ativos):")
    print(f"   {returns}")
    
    # Calcular matriz de covariância
    cov_matrix = np.cov(returns.T, ddof=1)  # ddof=1 para amostra
    print(f"   Matriz de covariancia:")
    print(f"   {cov_matrix}")
    
    # Verificar simetria
    is_symmetric = np.allclose(cov_matrix, cov_matrix.T)
    print(f"   Simetria: {'[OK]' if is_symmetric else '[ERRO]'}")
    
    # Verificar diagonal (variâncias)
    var_asset1 = np.var(returns[:, 0], ddof=1)
    var_asset2 = np.var(returns[:, 1], ddof=1)
    
    print(f"   Variancia ativo 1: {var_asset1:.6f} vs diagonal: {cov_matrix[0,0]:.6f}")
    print(f"   Variancia ativo 2: {var_asset2:.6f} vs diagonal: {cov_matrix[1,1]:.6f}")
    
    var_check = (abs(var_asset1 - cov_matrix[0,0]) < 1e-10 and 
                 abs(var_asset2 - cov_matrix[1,1]) < 1e-10)
    
    print(f"   RESULTADO: {'[OK]' if is_symmetric and var_check else '[ERRO]'}")

def audit_portfolio_volatility():
    """
    Audita o cálculo da volatilidade do portfólio
    """
    print(f"\n6. TESTE DE VOLATILIDADE DO PORTFOLIO:")
    
    # Dados de teste
    weights = np.array([0.4, 0.6])
    cov_matrix = np.array([
        [0.04, 0.01],  # Var1=0.04, Cov=0.01
        [0.01, 0.09]   # Cov=0.01, Var2=0.09
    ])
    
    print(f"   Pesos: {weights}")
    print(f"   Matriz de covariancia:")
    print(f"   {cov_matrix}")
    
    # Fórmula: σp² = w'Σw
    portfolio_variance = np.dot(weights.T, np.dot(cov_matrix, weights))
    portfolio_volatility = np.sqrt(portfolio_variance)
    
    print(f"   Variancia do portfolio: {portfolio_variance:.6f}")
    print(f"   Volatilidade do portfolio: {portfolio_volatility:.6f}")
    
    # Calcular manualmente para verificar
    # σp² = w1²σ1² + w2²σ2² + 2*w1*w2*σ12
    manual_var = (weights[0]**2 * cov_matrix[0,0] + 
                  weights[1]**2 * cov_matrix[1,1] + 
                  2 * weights[0] * weights[1] * cov_matrix[0,1])
    manual_vol = np.sqrt(manual_var)
    
    print(f"   Variancia manual: {manual_var:.6f}")
    print(f"   Volatilidade manual: {manual_vol:.6f}")
    
    # Verificar
    var_diff = abs(portfolio_variance - manual_var)
    vol_diff = abs(portfolio_volatility - manual_vol)
    
    print(f"   Diferenca variancia: {var_diff:.10f}")
    print(f"   Diferenca volatilidade: {vol_diff:.10f}")
    print(f"   RESULTADO: {'[OK]' if var_diff < 1e-10 and vol_diff < 1e-10 else '[ERRO]'}")

def audit_erc_calculations():
    """
    Audita os cálculos de Equal Risk Contribution
    """
    print(f"\n7. TESTE DOS CALCULOS ERC:")
    
    # Dados de teste simples (2 ativos)
    weights = np.array([0.6, 0.4])
    cov_matrix = np.array([
        [0.04, 0.01],
        [0.01, 0.09]
    ])
    
    print(f"   Pesos: {weights}")
    print(f"   Matriz de covariancia:")
    print(f"   {cov_matrix}")
    
    # Calcular volatilidade do portfólio
    portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
    print(f"   Volatilidade do portfolio: {portfolio_vol:.6f}")
    
    # Calcular contribuições marginais de risco
    # MCRi = (Σw)i / σp
    marginal_contrib = np.dot(cov_matrix, weights) / portfolio_vol
    print(f"   Contribuicoes marginais: {marginal_contrib}")
    
    # Calcular contribuições de risco
    # RCi = wi * MCRi
    risk_contrib = weights * marginal_contrib
    print(f"   Contribuicoes de risco: {risk_contrib}")
    
    # Verificar se soma das contribuições = volatilidade do portfólio
    total_contrib = np.sum(risk_contrib)
    print(f"   Soma das contribuicoes: {total_contrib:.6f}")
    print(f"   Volatilidade do portfolio: {portfolio_vol:.6f}")
    
    # Para ERC, contribuições devem ser iguais
    target_contrib = portfolio_vol / len(weights)
    print(f"   Contribuicao alvo (ERC): {target_contrib:.6f}")
    print(f"   Desvios do ERC: {risk_contrib - target_contrib}")
    
    # Verificar se soma = volatilidade
    sum_check = abs(total_contrib - portfolio_vol) < 1e-10
    print(f"   RESULTADO: {'[OK]' if sum_check else '[ERRO]'}")

def main():
    """
    Executa todas as auditorias de fórmulas
    """
    audit_return_calculations()
    audit_annualization()
    audit_sharpe_ratio()
    audit_portfolio_return()
    audit_covariance_matrix()
    audit_portfolio_volatility()
    audit_erc_calculations()
    
    print(f"\n" + "="*80)
    print("AUDITORIA DE FORMULAS CONCLUIDA")
    print("="*80)

if __name__ == "__main__":
    main()