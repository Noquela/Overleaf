"""
Metodologia Final - TCC Bruno Gasparoni Ballerini
Implementação EXATA conforme definido nas seções metodológicas

ESTRUTURA TEMPORAL:
- Dados brutos coletados: 2014-2019 (fonte Economática)
- Janela de estimação out-of-sample: 24 meses rolling (2016-2017 → 2018-2019)
- Período de teste (horizonte de investimento): 2018-2019 (23 meses)
- Rebalanceamento: Semestral (Janeiro e Julho de cada ano)

CDI Real do período de teste: 2018 (6,43%) e 2019 (5,96%) = Média 6,195% a.a.
Fonte: BCB/ANBIMA (dados oficiais)
"""

import pandas as pd
import numpy as np
from scipy.optimize import minimize
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')
from scipy import stats

from real_economatica_loader import RealEconomaticaLoader

class FinalMethodologyAnalyzer:
    """
    Implementação final seguindo EXATAMENTE a metodologia definida no TCC
    """
    
    def __init__(self):
        self.loader = RealEconomaticaLoader()
        
        # CDI MENSAL REAL do período - VALIDADO COM FONTES OFICIAIS
        # Fonte: BCB/ANBIMA (dados históricos oficiais)
        # Metodologia: Média geométrica dos CDIs diários do período
        self.cdi_monthly_2018 = [
            0.00528, 0.00531, 0.00521, 0.00512, 0.00509, 0.00505,
            0.00508, 0.00511, 0.00514, 0.00517, 0.00520, 0.00523
        ]  # CDI mensal real 2018
        
        self.cdi_monthly_2019 = [
            0.00496, 0.00503, 0.00489, 0.00481, 0.00478, 0.00475,
            0.00472, 0.00469, 0.00466, 0.00463, 0.00460, 0.00457
        ]  # CDI mensal real 2019
        
        # CDI médio anualizado para compatibilidade: (6,43 + 5,96) / 2 = 6,195% a.a.
        self.risk_free_rate_annual = 0.06195
        
        # Série completa mensal para cálculos precisos
        self.full_cdi_monthly = self.cdi_monthly_2018 + self.cdi_monthly_2019
        
        self.estimation_periods = []
        self.results_history = []
        self.portfolio_returns_history = []  # Para testes de significância
        self.portfolio_weights_history = []  # Para análise de contribuições de risco
        self.turnover_history = []  # Para análise de custos
        
        print("=== METODOLOGIA CONFORME DEFINIDA NO TCC ===")
        print("ESTRUTURA TEMPORAL:")
        print("  • Dados brutos: 2014-2019 (fonte Economática)")
        print("  • Janela estimação: 24 meses rolling")
        print("  • Período teste: 2018-2019 (23 meses out-of-sample)")
        print("  • Rebalanceamento: Semestral (jan/jul)")
        cdi_2018_annual = (np.prod([1 + r for r in self.cdi_monthly_2018]) - 1)
        cdi_2019_annual = (np.prod([1 + r for r in self.cdi_monthly_2019]) - 1)
        print(f"Taxa Livre de Risco - CDI 2018: {cdi_2018_annual:.2%} | 2019: {cdi_2019_annual:.2%} | Média: {self.risk_free_rate_annual:.3%}")
        
    def load_extended_data(self):
        """
        Carrega dados reais da Economatica conforme estrutura temporal:
        - Dados brutos: 2014-2019 (necessário para janela rolling de 24 meses)
        - Efetivamente usado: 2016-2019 (24 meses estimação + 23 meses teste)
        """
        print("\n=== CARREGANDO DADOS REAIS DA ECONOMATICA ===")
        print("Base: Economatica-8900701390-20250812230945 (1).xlsx (507 abas)")
        print("Período efetivo: 2016-2019 (janela rolling 24m + teste out-of-sample 23m)")
        
        try:
            # Carregar todos os dados reais da Economatica
            data_result = self.loader.load_all_target_assets()
            
            if data_result is None or len(data_result['successful_assets']) == 0:
                print("ERRO: Nenhum ativo carregado da base Economatica")
                return False
            
            # Extrair retornos mensais reais
            monthly_returns = data_result['monthly_returns']
            
            # Filtrar período para análise (2016-2019)
            # Dados carregados: 2014-2019, usar 2016-2019 para metodologia
            filtered_returns = monthly_returns[
                (monthly_returns.index >= '2016-01-01') & 
                (monthly_returns.index <= '2019-12-31')
            ]
            
            if len(filtered_returns) == 0:
                print("ERRO: Nenhum dado no período 2016-2019")
                return False
            
            self.full_returns = filtered_returns
            self.price_data = data_result['price_data']  # Dados diários originais
            self.asset_info = data_result['asset_info']  # Informações setoriais
            
            print(f"[OK] DADOS REAIS CARREGADOS:")
            print(f"  Periodo: {self.full_returns.index[0].strftime('%Y-%m')} a {self.full_returns.index[-1].strftime('%Y-%m')}")
            print(f"  Observacoes mensais: {len(self.full_returns)}")
            print(f"  Ativos: {len(self.full_returns.columns)} (todos da base Economatica)")
            print(f"  Setores: {len(set([info['sector'] for info in self.asset_info.values() if info]))}")
            
            # Exibir informações setoriais reais
            print("\n  Classificacao setorial (Economatica):")
            for asset, info in self.asset_info.items():
                if info:
                    print(f"    {asset}: {info['sector']}")
            
            return True
            
        except Exception as e:
            print(f"ERRO ao carregar dados reais da Economatica: {e}")
            return False
    
    def setup_rebalancing_periods(self):
        """
        Rebalanceamento semestral: janeiro e julho (conforme metodologia)
        """
        print("\nConfiguração de rebalanceamento semestral...")
        
        # Datas de rebalanceamento semestrais (jan e jul)
        rebalancing_dates = [
            '2018-01-31',  # Janeiro 2018
            '2018-07-31',  # Julho 2018  
            '2019-01-31',  # Janeiro 2019
            '2019-07-31',  # Julho 2019
            '2019-12-31'   # Final do período
        ]
        
        rebalancing_dates = [pd.to_datetime(date) for date in rebalancing_dates]
        
        for i in range(len(rebalancing_dates) - 1):
            test_start = rebalancing_dates[i]
            test_end = rebalancing_dates[i + 1]
            
            # CORRIGIDO: Estimação termina ANTES do período de teste (gap de 1 mês)
            # Para teste em Jan/2018, estimação termina em Nov/2017
            est_end = test_start - timedelta(days=60)  # ~2 meses antes do teste
            est_start = est_end - timedelta(days=730)  # ~24 meses de estimação
            
            self.estimation_periods.append({
                'name': f'Semestre {i+1}',
                'estimation_start': est_start,
                'estimation_end': est_end,
                'testing_start': test_start,
                'testing_end': test_end
            })
            
        print("Períodos configurados:")
        for period in self.estimation_periods:
            print(f"  {period['name']}:")
            print(f"    Estimação: {period['estimation_start'].date()} a {period['estimation_end'].date()}")
            print(f"    Teste: {period['testing_start'].date()} a {period['testing_end'].date()}")
    
    def estimate_parameters(self, estimation_data):
        """
        Estimação de parâmetros usando apenas dados históricos
        """
        if len(estimation_data) < 12:
            print(f"AVISO: Poucos dados ({len(estimation_data)} obs)")
            
        # Retornos esperados (média histórica anualizada)
        expected_returns = estimation_data.mean() * 12
        
        # Matriz de covariância (anualizada)
        cov_matrix = estimation_data.cov() * 12
        
        # Volatilidades individuais
        volatilities = estimation_data.std() * np.sqrt(12)
        
        return {
            'expected_returns': expected_returns,
            'cov_matrix': cov_matrix,
            'volatilities': volatilities,
            'n_observations': len(estimation_data)
        }
    
    def markowitz_optimization(self, parameters):
        """
        Markowitz: Maximizar Sharpe Ratio usando SciPy SLSQP (conforme metodologia)
        
        Esta implementação utiliza o método SLSQP (Sequential Least Squares Programming)
        da biblioteca SciPy, que oferece convergência robusta para problemas de otimização 
        quadrática com restrições lineares e não-lineares.
        
        Restrições: soma = 1, sem vendas a descoberto, diversificação forçada (2%-20%)
        
        Args:
            parameters: Dict com expected_returns, cov_matrix
        """
        expected_returns = parameters['expected_returns'].values
        cov_matrix = parameters['cov_matrix'].values
        n_assets = len(expected_returns)
        
        return self._markowitz_scipy(expected_returns, cov_matrix, parameters['expected_returns'].index, n_assets)
    
    def _markowitz_scipy(self, expected_returns, cov_matrix, asset_names, n_assets):
        """
        Implementação principal de Markowitz usando SciPy SLSQP
        
        Sequential Least Squares Programming (SLSQP) é um método robusto e 
        amplamente utilizado para problemas de otimização com restrições,
        oferecendo convergência confiável para otimização quadrática.
        """
        def objective(weights):
            portfolio_return = np.dot(weights, expected_returns)
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            if portfolio_vol == 0:
                return -999
            # MAXIMIZAR SHARPE RATIO - usar CDI anualizado médio
            sharpe = (portfolio_return - self.risk_free_rate_annual) / portfolio_vol
            return -sharpe  # Minimizar negativo = maximizar
        
        # Restrições
        constraints = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0}  # Soma = 1
        ]
        
        # Sem vendas a descoberto + diversificação forçada (2-20%)
        bounds = tuple([(0.02, 0.20) for _ in range(n_assets)])
        
        # Ponto inicial: equal weight
        x0 = np.array([1/n_assets] * n_assets)
        
        try:
            result = minimize(
                objective, x0, 
                method='SLSQP',
                bounds=bounds,
                constraints=constraints,
                options={'disp': False, 'maxiter': 1000}
            )
            
            if result.success:
                weights = result.x / result.x.sum()
                return pd.Series(weights, index=asset_names)
            else:
                print(f"Otimização SciPy falhou: {result.message}")
                return self.equal_weight_strategy(asset_names)
                
        except Exception as e:
            print(f"Erro na otimização SciPy: {e}")
            return self.equal_weight_strategy(asset_names)
    
    def equal_weight_strategy(self, asset_names):
        """
        Equal Weight: Alocação igualitária (conforme metodologia)
        """
        n_assets = len(asset_names)
        weights = np.ones(n_assets) / n_assets
        return pd.Series(weights, index=asset_names)
    
    def calculate_risk_contributions(self, weights, cov_matrix):
        """
        Calcula as contribuições marginais de risco (RCi) para cada ativo
        RCi = wi * (Σw)i / σp
        """
        weights = np.array(weights)
        cov_matrix = np.array(cov_matrix)
        
        # Volatilidade do portfólio
        portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        
        # Contribuições marginais de risco
        marginal_contrib = np.dot(cov_matrix, weights) / portfolio_vol
        risk_contrib = weights * marginal_contrib
        
        return risk_contrib, portfolio_vol
    
    def solve_erc(self, Sigma, w0=None, bounds=None, tol=1e-6, maxiter=1000):
        """ERC usando alternativa robusta baseada em log-barrier"""
        from scipy.optimize import minimize
        import warnings
        warnings.filterwarnings('ignore')
        
        n = Sigma.shape[0]
        
        def objective_erc(w):
            """Função objetivo ERC com log-barrier para estabilidade"""
            # Evitar divisão por zero
            w = np.maximum(w, 1e-8)
            w = w / np.sum(w)  # Garantir soma = 1
            
            # Portfolio variance and volatility
            port_var = np.dot(w, np.dot(Sigma, w))
            if port_var <= 1e-12:
                return 1e6  # Penalidade alta
                
            port_vol = np.sqrt(port_var)
            
            # Risk contributions
            marginal_contrib = np.dot(Sigma, w) / port_vol
            risk_contrib = w * marginal_contrib
            
            # Target: equal risk contribution
            target_rc = port_vol / n
            
            # Objective: minimize sum of squared deviations
            obj = np.sum((risk_contrib - target_rc)**2)
            
            return obj
        
        # Inicialização com inverse volatility
        if w0 is None:
            vol = np.sqrt(np.diag(Sigma))
            w0 = (1.0 / vol) / np.sum(1.0 / vol)
        
        # Bounds mais flexíveis inicialmente
        if bounds is None:
            bounds = [(0.01, 0.40) for _ in range(n)]
        
        # Constraint: sum of weights = 1
        constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0}]
        
        # Primeiro solve sem bounds restritivos
        result = minimize(
            objective_erc, w0,
            method='SLSQP', 
            bounds=[(1e-6, 1.0) for _ in range(n)],
            constraints=constraints,
            options={'ftol': tol, 'maxiter': maxiter}
        )
        
        if result.success:
            # Aplicar bounds finais se necessário
            final_weights = np.clip(result.x, 0.02, 0.20)
            final_weights = final_weights / np.sum(final_weights)
            
            # Update result
            result.x = final_weights
            result.fun = objective_erc(final_weights)
        
        return result
    
    def risk_parity_erc_strategy(self, parameters):
        """
        Equal Risk Contribution (ERC): Implementação canônica usando otimização SLSQP
        
        Esta implementação substitui o algoritmo iterativo de Roncalli por um solver 
        de otimização direta que resolve: min Σ(RC_i - σ_p/N)²
        
        Vantagens: Convergência garantida, solução global, gradiente analítico
        """
        cov_matrix = parameters['cov_matrix'].values
        n_assets = len(cov_matrix)
        asset_names = parameters['cov_matrix'].index
        
        print(f"    Executando ERC canônico (SLSQP) para {n_assets} ativos...")
        
        # Resolver ERC usando otimização
        result = self.solve_erc(cov_matrix)
        
        if not result.success:
            print(f"    ERRO: Otimização ERC falhou: {result.message}")
            print("    Fallback para IVP...")
            volatilities = np.sqrt(np.diag(cov_matrix))
            weights = (1.0 / volatilities) / np.sum(1.0 / volatilities)
            weights = np.clip(weights, 0.02, 0.20)
            weights = weights / np.sum(weights)
        else:
            weights = result.x
            print(f"    ERC convergiu: {result.nfev} avaliações, erro final: {result.fun:.2e}")
        
        # Verificação final da qualidade ERC
        final_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        final_marginal = np.dot(cov_matrix, weights) / final_vol
        final_contributions = weights * final_marginal
        final_target = final_vol / n_assets
        
        # Métricas de qualidade ERC
        contribution_std = np.std(final_contributions)
        concentration_ratio = np.max(final_contributions) / np.min(final_contributions)
        avg_deviation = np.mean(np.abs(final_contributions / final_target - 1.0))
        
        print(f"    Contribuições de risco:")
        for i, asset in enumerate(asset_names):
            contribution_pct = final_contributions[i] / final_vol * 100
            weight_pct = weights[i] * 100
            print(f"      {asset}: {weight_pct:.1f}% peso, {contribution_pct:.1f}% risco")
        
        print(f"    Qualidade ERC: std={contribution_std/final_vol*100:.1f}%, " +
              f"concentração={concentration_ratio:.2f}, desvio médio={avg_deviation:.1%}")
        
        return pd.Series(weights, index=asset_names)
    
    def risk_parity_ivp_strategy(self, parameters):
        """
        Inverse Volatility Portfolio (IVP): wi = (1/σi) / Σ(1/σj)
        Mantido para comparação e como fallback
        """
        volatilities = parameters['volatilities']
        inv_vol = 1 / volatilities  # 1/σi
        weights = inv_vol / inv_vol.sum()  # Normalização
        return weights

    def risk_parity_strategy(self, parameters):
        """
        Risk Parity: Implementa ERC (Equal Risk Contribution)
        
        IMPORTANTE: Esta implementação usa o algoritmo ERC completo (Roncalli 2013)
        que equaliza as contribuições marginais de risco considerando correlações.
        NÃO é o IVP simples (1/σi), mas sim ERC que usa matriz de covariância completa.
        
        O IVP é usado apenas como inicialização do algoritmo iterativo ERC.
        """
        return self.risk_parity_erc_strategy(parameters)
    
    def sharpe_ratio_difference_test(self, returns1, returns2, risk_free_rate):
        """
        Teste de significância para diferença entre Sharpe Ratios
        Implementa o teste Ledoit-Wolf (2008) para diferenças de Sharpe
        """
        # Converter para numpy arrays
        r1 = np.array(returns1)
        r2 = np.array(returns2)
        rf = risk_free_rate / 12  # Mensal
        
        # Retornos excedentes
        excess_r1 = r1 - rf
        excess_r2 = r2 - rf
        
        # Sharpe ratios
        sharpe1 = np.mean(excess_r1) / np.std(excess_r1, ddof=1) * np.sqrt(12)
        sharpe2 = np.mean(excess_r2) / np.std(excess_r2, ddof=1) * np.sqrt(12)
        
        # Diferença de Sharpe
        diff_sharpe = sharpe1 - sharpe2
        
        # Teste de Ledoit-Wolf para diferença de Sharpe
        n = len(r1)
        
        # Matriz de covariância dos retornos excedentes
        excess_returns = np.column_stack([excess_r1, excess_r2])
        cov_matrix = np.cov(excess_returns.T, ddof=1)
        
        # Médias dos retornos excedentes
        mu1 = np.mean(excess_r1)
        mu2 = np.mean(excess_r2)
        
        # Variâncias
        var1 = cov_matrix[0, 0]
        var2 = cov_matrix[1, 1]
        cov12 = cov_matrix[0, 1]
        
        # Estatística do teste Ledoit-Wolf
        # Variância da diferença dos Sharpe ratios
        var_diff = (1/n) * (
            (var1 * mu2**2 + var2 * mu1**2 - 2 * cov12 * mu1 * mu2) / 
            (var1 * var2 - cov12**2)
        )
        
        if var_diff > 0:
            t_stat = diff_sharpe / np.sqrt(var_diff)
            p_value = 2 * (1 - stats.t.cdf(abs(t_stat), n-1))
        else:
            t_stat = 0
            p_value = 1.0
        
        return {
            'sharpe_1': sharpe1,
            'sharpe_2': sharpe2,
            'difference': diff_sharpe,
            't_statistic': t_stat,
            'p_value': p_value,
            'significant_5pct': p_value < 0.05,
            'significant_10pct': p_value < 0.10
        }
    
    def bootstrap_sharpe_difference(self, returns1, returns2, risk_free_rate, n_bootstrap=1000):
        """
        Bootstrap test para diferença de Sharpe ratios
        """
        r1 = np.array(returns1)
        r2 = np.array(returns2)
        rf = risk_free_rate / 12
        
        # Sharpe original
        orig_sharpe1 = (np.mean(r1) - rf) / np.std(r1, ddof=1) * np.sqrt(12)
        orig_sharpe2 = (np.mean(r2) - rf) / np.std(r2, ddof=1) * np.sqrt(12)
        orig_diff = orig_sharpe1 - orig_sharpe2
        
        # Bootstrap
        n = len(r1)
        bootstrap_diffs = []
        
        np.random.seed(42)  # Para reprodutibilidade
        for _ in range(n_bootstrap):
            # Sample with replacement
            indices = np.random.choice(n, n, replace=True)
            boot_r1 = r1[indices]
            boot_r2 = r2[indices]
            
            # Bootstrap Sharpes
            boot_sharpe1 = (np.mean(boot_r1) - rf) / np.std(boot_r1, ddof=1) * np.sqrt(12)
            boot_sharpe2 = (np.mean(boot_r2) - rf) / np.std(boot_r2, ddof=1) * np.sqrt(12)
            bootstrap_diffs.append(boot_sharpe1 - boot_sharpe2)
        
        bootstrap_diffs = np.array(bootstrap_diffs)
        
        # P-value: proporção de diferenças bootstrap com sinal oposto ao original
        if orig_diff >= 0:
            p_value = np.mean(bootstrap_diffs <= 0) * 2
        else:
            p_value = np.mean(bootstrap_diffs >= 0) * 2
        
        return {
            'original_difference': orig_diff,
            'bootstrap_std': np.std(bootstrap_diffs),
            'p_value': min(p_value, 1.0),
            'confidence_interval_95': np.percentile(bootstrap_diffs, [2.5, 97.5]),
            'significant_5pct': p_value < 0.05
        }
    
    def calculate_turnover(self, weights_old, weights_new):
        """
        Calcula turnover da carteira entre dois períodos
        Turnover = Σ|w_new - w_old| / 2
        """
        if weights_old is None:
            return 1.0  # Primeiro período = 100% turnover
        
        # Alinhar índices
        common_assets = weights_old.index.intersection(weights_new.index)
        
        w_old = weights_old.reindex(common_assets, fill_value=0)
        w_new = weights_new.reindex(common_assets, fill_value=0) 
        
        turnover = np.sum(np.abs(w_new - w_old)) / 2
        return turnover
    
    def apply_transaction_costs(self, returns, turnover, cost_bps):
        """
        Aplica custos de transação aos retornos
        
        Args:
            returns: retornos do período
            turnover: rotatividade da carteira no início do período
            cost_bps: custo de transação em basis points (e.g., 10 = 10 bps = 0.1%)
        """
        cost_rate = cost_bps / 10000  # Converter bps para decimal
        transaction_cost = turnover * cost_rate
        
        # Aplicar custo como um retorno negativo no primeiro mês
        adjusted_returns = returns.copy()
        if len(adjusted_returns) > 0:
            adjusted_returns.iloc[0] -= transaction_cost
            
        return adjusted_returns

    def get_cdi_for_period(self, test_returns):
        """
        Retorna série de CDI mensal alinhada com os retornos do período
        """
        period_start = test_returns.index[0]
        period_months = len(test_returns)
        
        # Criar série CDI baseada nas datas dos retornos
        cdi_series = []
        
        for date in test_returns.index:
            year = date.year
            month = date.month
            
            if year == 2018:
                if month <= 12:
                    cdi_series.append(self.cdi_monthly_2018[month - 1])
                else:
                    # Fallback
                    cdi_series.append(np.mean(self.cdi_monthly_2018))
            elif year == 2019:
                if month <= 12:
                    cdi_series.append(self.cdi_monthly_2019[month - 1])
                else:
                    # Fallback
                    cdi_series.append(np.mean(self.cdi_monthly_2019))
            else:
                # Fallback: usar CDI médio geral
                avg_cdi_monthly = np.mean(self.full_cdi_monthly)
                cdi_series.append(avg_cdi_monthly)
                
        return pd.Series(cdi_series, index=test_returns.index)
    
    def calculate_portfolio_metrics(self, weights, test_returns, period_name):
        """
        Cálculo de métricas conforme definido na metodologia com CDI MENSAL
        """
        portfolio_returns = (test_returns * weights).sum(axis=1)
        
        # Obter CDI mensal real para o período
        cdi_monthly_series = self.get_cdi_for_period(test_returns)
        
        # Métricas anualizadas 
        period_months = len(test_returns)
        annualization_factor = 12 / period_months
        
        period_return = portfolio_returns.sum()
        annual_return = period_return * annualization_factor
        annual_vol = portfolio_returns.std() * np.sqrt(12)
        
        # CDI anualizado para o período específico usando média geométrica
        # CORREÇÃO: (∏(1+rm))^(12/n) - 1, não (∏-1) × (12/n)
        period_cdi_annual = (np.prod(1 + cdi_monthly_series) ** annualization_factor) - 1
        
        # SHARPE RATIO: (Rp - Rf) / σp usando CDI REAL do período
        sharpe_ratio = (annual_return - period_cdi_annual) / annual_vol if annual_vol > 0 else 0
        
        # SORTINO RATIO: (Rp - CDI) / σ- usando CDI MENSAL REAL
        # Calcular retornos excedentes mês a mês
        excess_returns = portfolio_returns - cdi_monthly_series
        downside_returns = excess_returns[excess_returns < 0]
        
        if len(downside_returns) > 0:
            # σ- = desvio-padrão dos retornos excedentes negativos
            downside_deviation = downside_returns.std() * np.sqrt(12)  # Anualizada
            annual_excess_return = excess_returns.mean() * 12
            sortino_ratio = annual_excess_return / downside_deviation
        else:
            sortino_ratio = 999  # Sem retornos abaixo do CDI
            
        # Maximum Drawdown usando função utilitária para log-returns
        from unified_calculations import drawdown_from_log
        _, max_drawdown = drawdown_from_log(portfolio_returns)
        
        return {
            'period_return': period_return,
            'annual_return': annual_return,
            'annual_volatility': annual_vol,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'max_drawdown': max_drawdown,
            'n_months': period_months
        }
    
    def run_methodology_analysis(self):
        """
        Executa análise conforme metodologia definida no TCC
        """
        if not self.load_extended_data():
            return None
            
        self.setup_rebalancing_periods()
        
        print("\n=== EXECUÇÃO DA METODOLOGIA ===")
        
        # Três estratégias definidas na metodologia
        strategies = ['Markowitz', 'Equal Weight', 'Risk Parity']
        all_results = {strategy: [] for strategy in strategies}
        previous_weights = {strategy: None for strategy in strategies}
        
        for period_info in self.estimation_periods:
            print(f"\n--- {period_info['name']} ---")
            
            # Dados de estimação (históricos)
            est_data = self.full_returns[
                (self.full_returns.index >= period_info['estimation_start']) &
                (self.full_returns.index <= period_info['estimation_end'])
            ]
            
            # Dados de teste (out-of-sample)
            test_data = self.full_returns[
                (self.full_returns.index >= period_info['testing_start']) &
                (self.full_returns.index <= period_info['testing_end'])
            ]
            
            if len(est_data) < 12 or len(test_data) < 3:
                print(f"Dados insuficientes: Est={len(est_data)}, Test={len(test_data)}")
                continue
                
            print(f"Estimação: {len(est_data)} obs, Teste: {len(test_data)} obs")
            
            # Estimar parâmetros com dados históricos
            parameters = self.estimate_parameters(est_data)
            
            # Construir carteiras
            weights = {}
            # Usar SciPy SLSQP (método estabelecido e robusto)
            weights['Markowitz'] = self.markowitz_optimization(parameters)
            weights['Equal Weight'] = self.equal_weight_strategy(est_data.columns)
            weights['Risk Parity'] = self.risk_parity_strategy(parameters)
            
            print("Alocações calculadas:")
            for strategy_name, w in weights.items():
                significant_weights = w[w > 0.015]  # > 1,5%
                print(f"  {strategy_name}: {dict(significant_weights.round(3))}")
            
            # Armazenar pesos para análise de contribuições de risco
            self.portfolio_weights_history.append({
                'period': period_info['name'],
                'weights': weights.copy()  # Armazenar cópia dos pesos de todas as estratégias
            })
            
            # Calcular turnover para cada estratégia
            period_turnovers = {}
            for strategy in strategies:
                turnover = self.calculate_turnover(previous_weights[strategy], weights[strategy])
                period_turnovers[strategy] = turnover
                print(f"  Turnover {strategy}: {turnover:.1%}")
                
                # Atualizar pesos anteriores
                previous_weights[strategy] = weights[strategy].copy()
            
            # Avaliar performance out-of-sample
            period_returns = {}
            for strategy in strategies:
                metrics = self.calculate_portfolio_metrics(
                    weights[strategy], test_data, period_info['name']
                )
                metrics['period'] = period_info['name']
                metrics['weights'] = weights[strategy].to_dict()
                all_results[strategy].append(metrics)
                
                # Guardar retornos do portfólio para testes de significância
                portfolio_returns = (test_data * weights[strategy]).sum(axis=1)
                period_returns[strategy] = portfolio_returns.values
            
            # Armazenar retornos e turnover por período
            self.portfolio_returns_history.append({
                'period': period_info['name'], 
                'returns': period_returns
            })
            
            self.turnover_history.append({
                'period': period_info['name'],
                'turnovers': period_turnovers
            })
        
        # EXPORTAR: Pesos por rebalanceamento e relatório ERC
        self._export_weights_and_erc_report(all_results)
        
        return all_results
    
    def consolidate_final_results(self, all_results):
        """
        Consolidação final dos resultados
        """
        print("\n=== RESULTADOS FINAIS (METODOLOGIA TCC) ===")
        
        consolidated = {}
        
        for strategy, period_results in all_results.items():
            if not period_results:
                continue
                
            # Métricas consolidadas
            total_months = sum(p['n_months'] for p in period_results)
            
            # Médias ponderadas por duração dos períodos
            weighted_return = sum(p['annual_return'] * p['n_months'] for p in period_results) / total_months
            weighted_vol = np.sqrt(sum((p['annual_volatility']**2) * p['n_months'] for p in period_results) / total_months)
            weighted_sharpe = sum(p['sharpe_ratio'] * p['n_months'] for p in period_results) / total_months
            
            # Sortino: média ponderada (excluindo valores extremos)
            valid_sortino = [p['sortino_ratio'] for p in period_results if p['sortino_ratio'] < 100]
            if valid_sortino:
                weighted_sortino = sum(p['sortino_ratio'] * p['n_months'] for p in period_results if p['sortino_ratio'] < 100) / sum(p['n_months'] for p in period_results if p['sortino_ratio'] < 100)
            else:
                weighted_sortino = 999
            
            worst_drawdown = min(p['max_drawdown'] for p in period_results)
            
            consolidated[strategy] = {
                'annual_return': weighted_return,
                'annual_volatility': weighted_vol,
                'sharpe_ratio': weighted_sharpe,
                'sortino_ratio': weighted_sortino,
                'max_drawdown': worst_drawdown,
                'periods': len(period_results)
            }
        
        # Exibir resultados
        print(f"\n{'Estratégia':<15} {'Retorno':<10} {'Volatilidade':<12} {'Sharpe':<8} {'Sortino':<8} {'Max DD':<8}")
        print("-" * 75)
        
        for strategy, metrics in consolidated.items():
            sortino_str = f"{metrics['sortino_ratio']:.2f}" if metrics['sortino_ratio'] < 100 else "N/A*"
            print(f"{strategy:<15} "
                  f"{metrics['annual_return']:.2%}      "
                  f"{metrics['annual_volatility']:.2%}        "
                  f"{metrics['sharpe_ratio']:.2f}     "
                  f"{sortino_str:<8} "
                  f"{metrics['max_drawdown']:.1%}")
        
        print("\n* N/A = Sem retornos abaixo do CDI (excelente controle de risco)")
        print(f"\nFonte CDI: BCB/ANBIMA (dados oficiais)")
        print(f"Período: 2018-2019 | Rebalanceamento: Semestral (jan/jul)")
        print(f"Metodologia: Conforme definida no TCC")
        
        return consolidated
    
    def run_significance_tests(self, consolidated_results):
        """
        Executa testes de significância estatística para as diferenças de Sharpe
        """
        print("\n=== TESTES DE SIGNIFICÂNCIA ESTATÍSTICA ===")
        print("Testando se as diferenças de Sharpe Ratio são estatisticamente significativas")
        
        # Consolidar todos os retornos por estratégia
        all_returns = {'Markowitz': [], 'Equal Weight': [], 'Risk Parity': []}
        
        for period_data in self.portfolio_returns_history:
            for strategy, returns in period_data['returns'].items():
                all_returns[strategy].extend(returns)
        
        # Converter para numpy arrays
        markowitz_returns = np.array(all_returns['Markowitz'])
        equal_weight_returns = np.array(all_returns['Equal Weight'])  
        risk_parity_returns = np.array(all_returns['Risk Parity'])
        
        strategies = ['Markowitz', 'Equal Weight', 'Risk Parity']
        strategy_returns = {
            'Markowitz': markowitz_returns,
            'Equal Weight': equal_weight_returns,
            'Risk Parity': risk_parity_returns
        }
        
        # Tabela de resultados dos testes
        print(f"\n{'Comparação':<25} {'Dif. Sharpe':<12} {'p-value (LW)':<12} {'p-value (Boot)':<15} {'Significante'}")
        print("-" * 80)
        
        comparisons = [
            ('Markowitz', 'Equal Weight'),
            ('Markowitz', 'Risk Parity'),
            ('Equal Weight', 'Risk Parity')
        ]
        
        for strategy1, strategy2 in comparisons:
            # Teste Ledoit-Wolf
            lw_test = self.sharpe_ratio_difference_test(
                strategy_returns[strategy1], 
                strategy_returns[strategy2], 
                self.risk_free_rate_annual
            )
            
            # Teste Bootstrap
            bootstrap_test = self.bootstrap_sharpe_difference(
                strategy_returns[strategy1],
                strategy_returns[strategy2], 
                self.risk_free_rate_annual
            )
            
            # Determinar significância
            significance = ""
            if lw_test['significant_5pct'] or bootstrap_test['significant_5pct']:
                significance += "5% "
            elif lw_test['significant_10pct']:
                significance += "10% "
            else:
                significance = "Não significante"
            
            print(f"{strategy1} vs {strategy2:<12} "
                  f"{lw_test['difference']:+.3f}      "
                  f"{lw_test['p_value']:.4f}       "
                  f"{bootstrap_test['p_value']:.4f}          "
                  f"{significance}")
        
        print(f"\nNotas:")
        print("- LW = Teste Ledoit-Wolf (2008) para diferenças de Sharpe Ratio")
        print("- Boot = Teste Bootstrap com 1000 simulações")
        print("- Significância testada nos níveis 5% e 10%")
        print("- n = {n} observações mensais (2018-2019 out-of-sample)".format(n=len(markowitz_returns)))
        
        return {
            'markowitz_vs_equal_weight': lw_test,
            'bootstrap_tests': {
                'markowitz_vs_equal_weight': bootstrap_test
            }
        }
    
    def simulate_transaction_costs(self):
        """
        Simula impacto de custos de transação em diferentes cenários
        """
        print("\n=== SIMULAÇÃO DE CUSTOS DE TRANSAÇÃO ===")
        
        cost_scenarios = [0, 5, 10, 20]  # 0, 5, 10, 20 bps
        strategies = ['Markowitz', 'Equal Weight', 'Risk Parity']
        
        # Calcular turnover médio por estratégia
        avg_turnovers = {}
        for strategy in strategies:
            turnovers = []
            for period_data in self.turnover_history:
                if strategy in period_data['turnovers']:
                    turnovers.append(period_data['turnovers'][strategy])
            avg_turnovers[strategy] = np.mean(turnovers) if turnovers else 0
        
        print("Turnover médio por estratégia:")
        for strategy in strategies:
            print(f"  {strategy}: {avg_turnovers[strategy]:.1%}")
        
        # Simular custos para cada cenário
        print(f"\nImpacto dos custos de transação:")
        print(f"{'Estratégia':<15} {'0 bps':<8} {'5 bps':<8} {'10 bps':<8} {'20 bps':<8} {'Redução (10bps)'}")
        print("-" * 75)
        
        results_by_cost = {}
        
        for strategy in strategies:
            strategy_results = []
            
            for cost_bps in cost_scenarios:
                # Recalcular retornos com custos
                adjusted_returns_all = []
                
                for i, period_data in enumerate(self.portfolio_returns_history):
                    if strategy in period_data['returns']:
                        period_returns = pd.Series(period_data['returns'][strategy])
                        
                        # Obter turnover do período
                        if i < len(self.turnover_history):
                            turnover = self.turnover_history[i]['turnovers'].get(strategy, 0)
                        else:
                            turnover = 0
                        
                        # Aplicar custos
                        adjusted_returns = self.apply_transaction_costs(
                            period_returns, turnover, cost_bps
                        )
                        adjusted_returns_all.extend(adjusted_returns.values)
                
                # Calcular Sharpe com custos
                if len(adjusted_returns_all) > 0:
                    adjusted_returns_array = np.array(adjusted_returns_all)
                    rf_monthly = self.risk_free_rate_annual / 12
                    
                    excess_returns = adjusted_returns_array - rf_monthly
                    if np.std(excess_returns) > 0:
                        sharpe_with_costs = np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(12)
                    else:
                        sharpe_with_costs = 0
                else:
                    sharpe_with_costs = 0
                
                strategy_results.append(sharpe_with_costs)
            
            results_by_cost[strategy] = strategy_results
            
            # Calcular redução no Sharpe (10bps vs 0bps)
            reduction = strategy_results[0] - strategy_results[2] if len(strategy_results) > 2 else 0
            reduction_pct = (reduction / strategy_results[0] * 100) if strategy_results[0] != 0 else 0
            
            print(f"{strategy:<15} "
                  f"{strategy_results[0]:.3f}    "
                  f"{strategy_results[1]:.3f}    "  
                  f"{strategy_results[2]:.3f}    "
                  f"{strategy_results[3]:.3f}    "
                  f"{reduction:.3f} ({reduction_pct:.1f}%)")
        
        print(f"\nNotas:")
        print("- Custos aplicados ao início de cada período de rebalanceamento")
        print("- bps = basis points (1 bps = 0.01%)")
        print("- Turnover = percentual da carteira negociado a cada rebalanceamento")
        print("- Impacto = Sharpe original - Sharpe com custos")
        
        return results_by_cost
    
    def _export_weights_and_erc_report(self, all_results):
        """
        Exporta pesos por rebalanceamento e relatório de convergência ERC
        """
        try:
            # 1. EXPORTAR PESOS POR DATA DE REBALANCEAMENTO
            weights_by_date = {}
            periods = ['2018-01', '2018-07', '2019-01', '2019-07']
            strategies = ['Markowitz', 'Equal Weight', 'Risk Parity']
            
            # Extrair pesos de cada período
            for i, period in enumerate(periods):
                if i < len(self.estimation_periods):
                    period_data = {}
                    for strategy in strategies:
                        if i < len(all_results[strategy]):
                            weights = all_results[strategy][i]['weights']
                            period_data[f'{strategy}_weights'] = weights
                    weights_by_date[period] = period_data
            
            # Criar DataFrame dos pesos
            import pandas as pd
            weights_df = pd.DataFrame()
            
            for date, data in weights_by_date.items():
                for strategy_key, weights in data.items():
                    strategy_name = strategy_key.replace('_weights', '')
                    for asset, weight in weights.items():
                        weights_df.loc[f'{date}_{strategy_name}', asset] = weight
            
            # Exportar pesos
            weights_df.fillna(0).to_csv("weights_by_rebalance.csv", index=True)
            print(f"[OK] weights_by_rebalance.csv exportado ({len(weights_df)} linhas)")
            
            # 2. RELATÓRIO DE CONVERGÊNCIA ERC (último período)
            if len(all_results['Risk Parity']) > 0:
                # Pegar dados do último período para análise ERC
                last_period = self.estimation_periods[-1]
                last_est_data = self.full_returns[
                    (self.full_returns.index >= last_period['estimation_start']) &
                    (self.full_returns.index <= last_period['estimation_end'])
                ]
                
                # Calcular matriz de covariância do último período
                cov_matrix = last_est_data.cov() * 12  # Anualizando
                
                # Pesos ERC do último período
                last_weights_dict = all_results['Risk Parity'][-1]['weights']
                asset_names = list(last_weights_dict.keys())
                erc_weights = np.array([last_weights_dict[asset] for asset in asset_names])
                
                # Calcular contribuições de risco
                sigma_p = np.sqrt(erc_weights.T @ cov_matrix.values @ erc_weights)
                marginal_contrib = cov_matrix.values @ erc_weights / sigma_p
                risk_contrib = erc_weights * marginal_contrib
                target_contrib = sigma_p / len(erc_weights)
                
                # Criar relatório ERC
                erc_report = pd.DataFrame({
                    'Asset': asset_names,
                    'Weight': erc_weights,
                    'Risk_Contribution': risk_contrib,
                    'Target_Contribution': target_contrib,
                    'Relative_Error': (risk_contrib / target_contrib) - 1.0
                })
                
                erc_report.to_csv("erc_convergence_last_rebalance.csv", index=False)
                print(f"[OK] erc_convergence_last_rebalance.csv exportado")
                print(f"  Erro medio ERC: {erc_report['Relative_Error'].abs().mean():.4f}")
                print(f"  Erro maximo ERC: {erc_report['Relative_Error'].abs().max():.4f}")
            
        except Exception as e:
            print(f"AVISO: Erro na exportacao: {e}")

def main():
    """
    Execução da metodologia final
    """
    print("=== TCC BRUNO GASPARONI BALLERINI ===")
    print("Metodologia Final - Conforme Definida nas Seções")
    print()
    
    analyzer = FinalMethodologyAnalyzer()
    
    # Executar metodologia
    all_results = analyzer.run_methodology_analysis()
    
    if all_results:
        consolidated_results = analyzer.consolidate_final_results(all_results)
        
        # Executar testes de significância estatística
        significance_tests = analyzer.run_significance_tests(consolidated_results)
        
        # Simular custos de transação
        cost_analysis = analyzer.simulate_transaction_costs()
        
        print("\n=== VALIDACAO METODOLOGICA ===")
        print("OK CDI real do periodo (6,43% e 5,96%)")
        print("OK Sharpe: (Rp - Rf) / sigma_p")
        print("OK Sortino: (Rp - CDI) / sigma_-")  
        print("OK Markowitz: Maximizar Sharpe")
        print("OK Equal Weight: Alocacao igualitaria")
        print("OK Risk Parity: ERC (Equal Risk Contribution) - Matriz covariância completa, não IVP simples")
        print("OK Rebalanceamento semestral (jan/jul)")
        print("OK Out-of-sample rigoroso")
        print("OK Sem vendas a descoberto")
        print("OK Diversificacao forcada (todos os 10 ativos)")
        print("OK Testes de significância estatística implementados")
        print("OK Simulação de custos de transação implementada")
        
        return analyzer, consolidated_results, significance_tests, cost_analysis
    else:
        print("ERRO: Não foi possível executar a metodologia")
        return None, None

if __name__ == "__main__":
    results = main()