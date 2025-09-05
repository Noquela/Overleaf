"""
AUDITORIA COMPLETA DOS DADOS DA ECONOMATICA
==========================================

Este script faz uma auditoria detalhada dos dados para garantir que tudo está correto.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os
import warnings
warnings.filterwarnings('ignore')

def audit_economatica_files():
    """
    Audita os arquivos da Economatica para verificar estrutura e conteúdo
    """
    print("="*80)
    print("AUDITORIA COMPLETA DOS DADOS DA ECONOMATICA")
    print("="*80)
    
    base_path = os.path.join(os.path.dirname(__file__), "..", "data", "DataBase")
    
    # Arquivo 1: Dados de preços
    price_file = os.path.join(base_path, "Economatica-8900701390-20250812230945 (1).xlsx")
    sector_file = os.path.join(base_path, "economatica (1).xlsx")
    
    print(f"\n1. VERIFICANDO ARQUIVO DE PRECOS:")
    print(f"   Path: {price_file}")
    print(f"   Existe: {os.path.exists(price_file)}")
    
    if os.path.exists(price_file):
        # Listar todas as abas
        xl_file = pd.ExcelFile(price_file)
        sheet_names = xl_file.sheet_names
        print(f"   Total de abas: {len(sheet_names)}")
        print(f"   Primeiras 10 abas: {sheet_names[:10]}")
        print(f"   Ultimas 10 abas: {sheet_names[-10:]}")
        
        # Verificar se os 10 ativos alvo estão presentes
        target_assets = ['PETR4', 'VALE3', 'ITUB4', 'BBDC4', 'ABEV3', 
                        'B3SA3', 'WEGE3', 'RENT3', 'LREN3', 'ELET3']
        
        print(f"\n   VERIFICACAO DOS 10 ATIVOS ALVO:")
        for asset in target_assets:
            present = asset in sheet_names
            print(f"     {asset}: {'[OK]' if present else '[ERRO] NAO ENCONTRADO'}")
        
        # Examinar estrutura de dados de um ativo
        if 'PETR4' in sheet_names:
            print(f"\n   EXAMINANDO ESTRUTURA DE DADOS (PETR4):")
            df_petr4 = pd.read_excel(price_file, sheet_name='PETR4')
            print(f"     Dimensoes: {df_petr4.shape}")
            print(f"     Primeiras 10 linhas:")
            print(df_petr4.head(10).to_string())
            
            print(f"\n     Linha 3 (onde devem comecar os dados):")
            if len(df_petr4) > 3:
                print(df_petr4.iloc[3:8].to_string())
    
    print(f"\n2. VERIFICANDO ARQUIVO DE SETORES:")
    print(f"   Path: {sector_file}")
    print(f"   Existe: {os.path.exists(sector_file)}")
    
    if os.path.exists(sector_file):
        xl_file = pd.ExcelFile(sector_file)
        sheet_names = xl_file.sheet_names
        print(f"   Abas disponiveis: {sheet_names}")
        
        # Examinar a aba principal
        if 'Sheet1' in sheet_names:
            print(f"\n   EXAMINANDO DADOS DE SETORES:")
            df_sectors = pd.read_excel(sector_file, sheet_name='Sheet1')
            print(f"     Dimensoes: {df_sectors.shape}")
            print(f"     Primeiras 10 linhas:")
            print(df_sectors.head(10).to_string())
            
            print(f"\n     Linha 3 (onde devem comecar os dados):")
            if len(df_sectors) > 3:
                print(df_sectors.iloc[3:8].to_string())

def audit_data_quality():
    """
    Testa a qualidade dos dados carregados pelo loader
    """
    print(f"\n3. AUDITORIA DE QUALIDADE DOS DADOS:")
    
    try:
        from real_economatica_loader import RealEconomaticaLoader
        loader = RealEconomaticaLoader()
        
        # Carregar um ativo de teste
        print(f"\n   TESTANDO CARREGAMENTO DE PETR4:")
        petr4_data = loader.load_asset_price_data('PETR4')
        
        if petr4_data is not None:
            print(f"     [OK] PETR4 carregado com sucesso")
            print(f"     Periodo: {petr4_data.index[0]} a {petr4_data.index[-1]}")
            print(f"     Observacoes: {len(petr4_data)}")
            print(f"     Colunas: {list(petr4_data.columns)}")
            
            # Verificar dados válidos
            print(f"\n     VERIFICACAO DE QUALIDADE:")
            print(f"     Valores nulos em Close: {petr4_data['Close'].isnull().sum()}")
            print(f"     Valores negativos em Close: {(petr4_data['Close'] <= 0).sum()}")
            print(f"     Preco minimo: {petr4_data['Close'].min():.4f}")
            print(f"     Preco maximo: {petr4_data['Close'].max():.4f}")
            print(f"     Preco medio: {petr4_data['Close'].mean():.4f}")
            
            # Verificar retornos
            returns = petr4_data['Returns'].dropna()
            print(f"\n     RETORNOS CALCULADOS:")
            print(f"     Retornos validos: {len(returns)}")
            print(f"     Retorno medio diario: {returns.mean():.6f}")
            print(f"     Volatilidade diaria: {returns.std():.6f}")
            print(f"     Retorno anualizado: {returns.mean() * 252:.4f}")
            print(f"     Volatilidade anualizada: {returns.std() * np.sqrt(252):.4f}")
            
        else:
            print(f"     [ERRO] Falha ao carregar PETR4")
            
    except Exception as e:
        print(f"     [ERRO] Erro no teste: {e}")

def audit_full_dataset():
    """
    Audita o dataset completo
    """
    print(f"\n4. AUDITORIA DO DATASET COMPLETO:")
    
    try:
        from real_economatica_loader import RealEconomaticaLoader
        loader = RealEconomaticaLoader()
        
        print(f"\n   CARREGANDO TODOS OS ATIVOS...")
        result = loader.load_all_target_assets()
        
        if result:
            monthly_returns = result['monthly_returns']
            print(f"     [OK] Dataset completo carregado")
            print(f"     Dimensoes: {monthly_returns.shape}")
            print(f"     Periodo: {monthly_returns.index[0]} a {monthly_returns.index[-1]}")
            print(f"     Ativos: {list(monthly_returns.columns)}")
            
            # Estatísticas por ativo
            print(f"\n     ESTATISTICAS POR ATIVO (2014-2019):")
            print(f"     {'Ativo':<8} {'N Obs':<6} {'Ret Anual':<10} {'Vol Anual':<10} {'Sharpe':<8}")
            print(f"     {'-'*50}")
            
            for asset in monthly_returns.columns:
                asset_returns = monthly_returns[asset].dropna()
                if len(asset_returns) > 0:
                    annual_ret = asset_returns.mean() * 12
                    annual_vol = asset_returns.std() * np.sqrt(12)
                    sharpe = annual_ret / annual_vol if annual_vol > 0 else 0
                    
                    print(f"     {asset:<8} {len(asset_returns):<6} {annual_ret:<10.3f} {annual_vol:<10.3f} {sharpe:<8.3f}")
            
            # Matriz de correlação
            print(f"\n     MATRIZ DE CORRELACAO:")
            corr_matrix = monthly_returns.corr()
            print(corr_matrix.round(3).to_string())
            
            # Verificar dados missing
            print(f"\n     VERIFICACAO DE DADOS FALTANTES:")
            missing_data = monthly_returns.isnull().sum()
            if missing_data.sum() > 0:
                print(f"     ATENCAO: Dados faltantes encontrados:")
                for asset, missing in missing_data.items():
                    if missing > 0:
                        print(f"       {asset}: {missing} observacoes faltantes")
            else:
                print(f"     [OK] Nenhum dado faltante encontrado")
                
        else:
            print(f"     [ERRO] Falha ao carregar dataset completo")
            
    except Exception as e:
        print(f"     [ERRO] Erro na auditoria: {e}")
        import traceback
        traceback.print_exc()

def main():
    """
    Executa auditoria completa
    """
    audit_economatica_files()
    audit_data_quality() 
    audit_full_dataset()
    
    print(f"\n" + "="*80)
    print("AUDITORIA CONCLUIDA")
    print("="*80)

if __name__ == "__main__":
    main()