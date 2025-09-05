"""
LOADER DE DADOS REAIS DA ECONOMATICA
====================================

Este módulo carrega EXCLUSIVAMENTE dados reais da base da Economatica.
Sem fallbacks, sem dados simulados - apenas dados reais conforme exigido.

Autor: Bruno Gasparoni Ballerini
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class RealEconomaticaLoader:
    """
    Carregador que usa APENAS dados reais da Economatica
    """
    
    def __init__(self):
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # PATHS DA BASE REAL DA ECONOMATICA
        self.price_data_path = os.path.join(current_dir, "..", "data", "DataBase", 
                                          "Economatica-8900701390-20250812230945 (1).xlsx")
        self.sector_data_path = os.path.join(current_dir, "..", "data", "DataBase", 
                                           "economatica (1).xlsx")
        
        # ATIVOS ALVO (validados como existentes na base)
        self.target_assets = ['PETR4', 'VALE3', 'ITUB4', 'BBDC4', 'ABEV3', 
                             'B3SA3', 'WEGE3', 'RENT3', 'LREN3', 'ELET3']
        
        # Cache de dados carregados
        self._price_data_cache = {}
        self._sector_data_cache = None
        
    def load_asset_price_data(self, asset_code):
        """
        Carrega dados de preços de um ativo específico da base real da Economatica
        """
        if asset_code in self._price_data_cache:
            return self._price_data_cache[asset_code]
            
        try:
            print(f"Carregando dados reais de {asset_code} da Economatica...")
            
            # Carregar aba específica do ativo
            df = pd.read_excel(self.price_data_path, sheet_name=asset_code)
            
            # Extrair dados a partir da linha 3 (onde começam os dados reais)
            # Estrutura: Data | Q Negs | Q Tots | Volume$ | Fechamento | Abertura | Mínimo | Máximo | Médio
            data_start_row = 3
            price_data = df.iloc[data_start_row:].copy()
            
            # Definir colunas corretas
            price_data.columns = ['Date', 'Q_Trades', 'Q_Total', 'Volume_BRL', 
                                'Close', 'Open', 'Low', 'High', 'Average']
            
            # Converter data e limpar dados
            price_data['Date'] = pd.to_datetime(price_data['Date'], errors='coerce')
            
            # Converter preços para numérico (lidar com strings)
            numeric_columns = ['Close', 'Open', 'High', 'Low', 'Volume_BRL']
            for col in numeric_columns:
                price_data[col] = pd.to_numeric(price_data[col], errors='coerce')
            
            # Remover linhas com dados inválidos
            price_data = price_data.dropna(subset=['Date', 'Close'])
            
            # Filtrar período de interesse (2014-2019)
            price_data = price_data[
                (price_data['Date'] >= '2014-01-01') & 
                (price_data['Date'] <= '2019-12-31')
            ].copy()
            
            # Calcular retornos logarítmicos
            price_data = price_data.sort_values('Date')
            price_data['Returns'] = np.log(price_data['Close'] / price_data['Close'].shift(1))
            
            # Set index como data
            price_data.set_index('Date', inplace=True)
            
            print(f"  [OK] {asset_code}: {len(price_data)} observações de {price_data.index.min()} a {price_data.index.max()}")
            
            # Cache dos dados
            self._price_data_cache[asset_code] = price_data
            
            return price_data
            
        except Exception as e:
            print(f"ERRO ao carregar {asset_code}: {str(e)}")
            return None
    
    def load_sector_data(self):
        """
        Carrega dados de setores da base real da Economatica
        """
        if self._sector_data_cache is not None:
            return self._sector_data_cache
            
        try:
            print("Carregando dados de setores da Economatica...")
            
            df = pd.read_excel(self.sector_data_path, sheet_name='Sheet1')
            
            # Extrair dados a partir da linha 3 (onde começam os dados reais)
            sector_data = df.iloc[3:].copy()
            sector_data.columns = ['ID', 'Company', 'Class', 'Exchange', 'Asset_Type', 
                                 'Active', 'Code', 'Sector_Economatica', 
                                 'Sector_Economic_Bovespa', 'Segment_Bovespa']
            
            # Cache dos dados
            self._sector_data_cache = sector_data
            
            print(f"  [OK] Dados de setores: {len(sector_data)} empresas")
            
            return sector_data
            
        except Exception as e:
            print(f"ERRO ao carregar dados de setores: {str(e)}")
            return None
    
    def get_asset_sector_info(self, asset_code):
        """
        Retorna informações de setor para um ativo específico
        """
        sector_data = self.load_sector_data()
        if sector_data is None:
            return None
            
        # Mapeamento manual baseado na análise da base real
        asset_sector_mapping = {
            'PETR4': {'company': 'Petrobras', 'class': 'PN', 'sector': 'Exploração refino e distribuição'},
            'VALE3': {'company': 'Vale', 'class': 'ON', 'sector': 'Minerais metálicos'},
            'ITUB4': {'company': 'ItauUnibanco', 'class': 'PN', 'sector': 'Bancos'},
            'BBDC4': {'company': 'Bradesco', 'class': 'PN', 'sector': 'Bancos'},
            'ABEV3': {'company': 'Ambev S/A', 'class': 'ON', 'sector': 'Cervejas e refrigerantes'},
            'B3SA3': {'company': 'B3', 'class': 'ON', 'sector': 'Serviços financeiros diversos'},
            'WEGE3': {'company': 'Weg', 'class': 'ON', 'sector': 'Motores compressores e outros'},
            'RENT3': {'company': 'Localiza', 'class': 'ON', 'sector': 'Aluguel de carros'},
            'LREN3': {'company': 'Lojas Renner', 'class': 'ON', 'sector': 'Tecidos vestuário e calçados'},
            'ELET3': {'company': 'Eletrobras', 'class': 'ON', 'sector': 'Energia elétrica'}
        }
        
        return asset_sector_mapping.get(asset_code)
    
    def load_all_target_assets(self):
        """
        Carrega dados de preços de todos os ativos alvo
        """
        print("=== CARREGANDO DADOS REAIS DA ECONOMATICA ===")
        print("Base: Economatica-8900701390-20250812230945 (1).xlsx (507 abas)")
        print(f"Ativos alvo: {self.target_assets}")
        print()
        
        all_data = {}
        successful_assets = []
        
        for asset in self.target_assets:
            data = self.load_asset_price_data(asset)
            if data is not None and len(data) > 0:
                all_data[asset] = data
                successful_assets.append(asset)
                
                # Exibir informações do setor
                sector_info = self.get_asset_sector_info(asset)
                if sector_info:
                    print(f"  Setor: {sector_info['sector']}")
            else:
                print(f"  [ERRO] FALHOU ao carregar {asset}")
        
        print(f"\n=== RESUMO ===")
        print(f"Ativos carregados com sucesso: {len(successful_assets)}/10")
        print(f"Ativos: {successful_assets}")
        
        # Criar DataFrame consolidado com retornos mensais
        if successful_assets:
            monthly_returns = self.calculate_monthly_returns(all_data)
            print(f"Retornos mensais: {monthly_returns.shape}")
            print(f"Período: {monthly_returns.index.min()} a {monthly_returns.index.max()}")
            
            return {
                'price_data': all_data,
                'monthly_returns': monthly_returns,
                'successful_assets': successful_assets,
                'asset_info': {asset: self.get_asset_sector_info(asset) for asset in successful_assets}
            }
        else:
            raise RuntimeError("FALHA CRÍTICA: Nenhum ativo foi carregado com sucesso da base da Economatica")
    
    def calculate_monthly_returns(self, price_data):
        """
        Calcula retornos mensais a partir dos dados diários
        """
        monthly_returns_dict = {}
        
        for asset, data in price_data.items():
            # Reamostrar para dados mensais (último dia útil do mês)
            monthly_prices = data['Close'].resample('M').last()
            
            # Calcular retornos logarítmicos mensais
            monthly_returns = np.log(monthly_prices / monthly_prices.shift(1)).dropna()
            
            monthly_returns_dict[asset] = monthly_returns
        
        # Consolidar em DataFrame
        monthly_df = pd.DataFrame(monthly_returns_dict)
        
        # Remover NaNs e alinhar datas
        monthly_df = monthly_df.dropna()
        
        return monthly_df

def main():
    """
    Teste do carregador de dados reais
    """
    loader = RealEconomaticaLoader()
    
    try:
        result = loader.load_all_target_assets()
        print("\n[OK] SUCESSO: Base real da Economatica carregada!")
        
        # Estatísticas dos dados carregados
        monthly_returns = result['monthly_returns']
        print(f"\nEstatísticas dos retornos mensais:")
        print(f"Período: {monthly_returns.index[0].strftime('%Y-%m')} a {monthly_returns.index[-1].strftime('%Y-%m')}")
        print(f"Observações: {len(monthly_returns)} meses")
        print(f"Ativos: {len(monthly_returns.columns)} ativos")
        
        # Exibir retornos anualizados
        print(f"\nRetornos anualizados (%):")
        annual_returns = (monthly_returns.mean() * 12 * 100).round(2)
        for asset, ret in annual_returns.items():
            sector = result['asset_info'][asset]['sector'] if result['asset_info'][asset] else 'N/A'
            print(f"  {asset}: {ret:6.2f}% ({sector})")
        
    except Exception as e:
        print(f"\n[ERRO]: {e}")

if __name__ == "__main__":
    main()