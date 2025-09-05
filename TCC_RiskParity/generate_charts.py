#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para gerar gráficos do TCC com dados reais validados
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import os

# Configurar matplotlib
plt.rcParams['font.size'] = 10
plt.rcParams['figure.figsize'] = [12, 8]
sns.set_style("whitegrid")

# Dados validados das tabelas já corrigidas
print("=== GERANDO GRÁFICOS COM DADOS REAIS VALIDADOS ===")

# Diretório de saída
output_dir = "docs/Overleaf/images"
os.makedirs(output_dir, exist_ok=True)

# 1. DADOS DOS ATIVOS (da tabela descriptive_stats validada)
asset_data = {
    'PETR4': {'setor': 'Exploração refino', 'retorno': 5.8, 'volatilidade': 28.4, 'sharpe': -0.02},
    'VALE3': {'setor': 'Minerais metálicos', 'retorno': 19.2, 'volatilidade': 26.1, 'sharpe': 0.49},
    'ITUB4': {'setor': 'Bancos', 'retorno': 8.6, 'volatilidade': 21.2, 'sharpe': 0.11},
    'BBDC4': {'setor': 'Bancos', 'retorno': 12.4, 'volatilidade': 23.8, 'sharpe': 0.26},
    'ABEV3': {'setor': 'Cervejas/refrigerantes', 'retorno': 23.1, 'volatilidade': 19.6, 'sharpe': 0.86},
    'B3SA3': {'setor': 'Serviços financeiros', 'retorno': 31.8, 'volatilidade': 25.4, 'sharpe': 1.01},
    'WEGE3': {'setor': 'Motores/compressores', 'retorno': 42.6, 'volatilidade': 23.9, 'sharpe': 1.53},
    'RENT3': {'setor': 'Aluguel de carros', 'retorno': 38.2, 'volatilidade': 26.8, 'sharpe': 1.19},
    'LREN3': {'setor': 'Tecidos/vestuário', 'retorno': 29.4, 'volatilidade': 24.7, 'sharpe': 0.94},
    'ELET3': {'setor': 'Energia elétrica', 'retorno': 26.8, 'volatilidade': 22.3, 'sharpe': 0.93}
}

# 2. DADOS DAS ESTRATÉGIAS (validados da metodologia)
strategy_data = {
    'Markowitz': {'retorno': 32.61, 'volatilidade': 16.68, 'sharpe': 2.38, 'sortino': 11.32, 'drawdown': -14.6},
    'Equal Weight': {'retorno': 35.93, 'volatilidade': 22.02, 'sharpe': 1.86, 'sortino': 2.85, 'drawdown': -18.7},
    'Risk Parity': {'retorno': 29.53, 'volatilidade': 18.48, 'sharpe': 1.84, 'sortino': 12.33, 'drawdown': -17.9}
}

print("1. Análise Setorial por Ativo...")
# GRÁFICO 1: ANÁLISE SETORIAL
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

# Ordenar por retorno
assets_sorted = sorted(asset_data.items(), key=lambda x: x[1]['retorno'], reverse=True)
assets = [item[0] for item in assets_sorted]
returns = [item[1]['retorno'] for item in assets_sorted]
setores = [item[1]['setor'] for item in assets_sorted]

# Gráfico de barras - Retorno por ativo
colors = plt.cm.RdYlGn(np.linspace(0.3, 0.9, len(assets)))
bars = ax1.barh(range(len(assets)), returns, color=colors, alpha=0.8)
ax1.set_yticks(range(len(assets)))
ax1.set_yticklabels([f'{asset}\n({setor})' for asset, setor in zip(assets, setores)], fontsize=9)
ax1.set_xlabel('Retorno Anualizado (%)', fontsize=12)
ax1.set_title('Retorno por Ativo e Setor (2018-2019)', fontsize=14, fontweight='bold', pad=20)
ax1.grid(True, alpha=0.3)

# Adicionar valores nas barras
for i, (bar, ret) in enumerate(zip(bars, returns)):
    width = bar.get_width()
    ax1.text(width + 0.5, bar.get_y() + bar.get_height()/2, 
             f'{ret:.1f}%', ha='left', va='center', fontweight='bold')

# Gráfico de dispersão - Risco vs Retorno
volatilidades = [asset_data[asset]['volatilidade'] for asset in assets]
scatter = ax2.scatter(volatilidades, returns, c=returns, cmap='RdYlGn', s=120, alpha=0.8, edgecolors='black')
ax2.set_xlabel('Volatilidade Anualizada (%)', fontsize=12)
ax2.set_ylabel('Retorno Anualizado (%)', fontsize=12)
ax2.set_title('Risco vs. Retorno dos Ativos', fontsize=14, fontweight='bold', pad=20)
ax2.grid(True, alpha=0.3)

# Adicionar labels nos pontos
for asset, vol, ret in zip(assets, volatilidades, returns):
    ax2.annotate(asset, (vol, ret), xytext=(5, 5), textcoords='offset points', 
                fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig(f'{output_dir}/sector_analysis.png', dpi=300, bbox_inches='tight')
plt.close()

print("2. Performance das Estratégias...")
# GRÁFICO 2: PERFORMANCE DAS ESTRATÉGIAS
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

strategies = list(strategy_data.keys())
colors_strat = ['#2E8B57', '#FF6347', '#4682B4']  # Verde, Vermelho, Azul

# Retorno
returns_strat = [strategy_data[s]['retorno'] for s in strategies]
bars1 = ax1.bar(strategies, returns_strat, color=colors_strat, alpha=0.8, edgecolor='black')
ax1.set_ylabel('Retorno Anualizado (%)')
ax1.set_title('Retorno das Estratégias', fontweight='bold')
ax1.grid(True, alpha=0.3)
for bar, ret in zip(bars1, returns_strat):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
             f'{ret:.1f}%', ha='center', va='bottom', fontweight='bold')

# Sharpe Ratio
sharpes = [strategy_data[s]['sharpe'] for s in strategies]
bars2 = ax2.bar(strategies, sharpes, color=colors_strat, alpha=0.8, edgecolor='black')
ax2.set_ylabel('Sharpe Ratio')
ax2.set_title('Índice de Sharpe', fontweight='bold')
ax2.grid(True, alpha=0.3)
for bar, sharpe in zip(bars2, sharpes):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05, 
             f'{sharpe:.2f}', ha='center', va='bottom', fontweight='bold')

# Volatilidade
vols = [strategy_data[s]['volatilidade'] for s in strategies]
bars3 = ax3.bar(strategies, vols, color=colors_strat, alpha=0.8, edgecolor='black')
ax3.set_ylabel('Volatilidade Anualizada (%)')
ax3.set_title('Volatilidade das Estratégias', fontweight='bold')
ax3.grid(True, alpha=0.3)
for bar, vol in zip(bars3, vols):
    ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3, 
             f'{vol:.1f}%', ha='center', va='bottom', fontweight='bold')

# Risco vs Retorno das Estratégias
scatter_strat = ax4.scatter(vols, returns_strat, c=colors_strat, s=200, alpha=0.8, edgecolors='black')
ax4.set_xlabel('Volatilidade Anualizada (%)')
ax4.set_ylabel('Retorno Anualizado (%)')
ax4.set_title('Risco vs. Retorno das Estratégias', fontweight='bold')
ax4.grid(True, alpha=0.3)

for i, strat in enumerate(strategies):
    ax4.annotate(strat, (vols[i], returns_strat[i]), 
                xytext=(5, 5), textcoords='offset points', 
                fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig(f'{output_dir}/portfolio_performance.png', dpi=300, bbox_inches='tight')
plt.close()

print("3. Gráfico Risk-Return Plot...")
# GRÁFICO 3: RISK-RETURN PLOT ESPECÍFICO
plt.figure(figsize=(10, 8))
scatter = plt.scatter(vols, returns_strat, c=colors_strat, s=300, alpha=0.8, edgecolors='black', linewidth=2)

plt.xlabel('Volatilidade Anualizada (%)', fontsize=14)
plt.ylabel('Retorno Anualizado (%)', fontsize=14)
plt.title('Posicionamento das Estratégias no Plano Risco-Retorno', fontsize=16, fontweight='bold', pad=20)
plt.grid(True, alpha=0.3)

# Adicionar labels
for i, strat in enumerate(strategies):
    plt.annotate(strat, (vols[i], returns_strat[i]), 
                xytext=(10, 10), textcoords='offset points', 
                fontsize=12, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))

# Adicionar linha de CDI
plt.axhline(y=6.195, color='red', linestyle='--', alpha=0.7, label='CDI (6,195%)')
plt.legend(fontsize=12)

plt.tight_layout()
plt.savefig(f'{output_dir}/risk_return_plot.png', dpi=300, bbox_inches='tight')
plt.close()

print("✅ GRÁFICOS GERADOS COM SUCESSO!")
print(f"- {output_dir}/sector_analysis.png")
print(f"- {output_dir}/portfolio_performance.png") 
print(f"- {output_dir}/risk_return_plot.png")
print("\n📊 Todos os gráficos foram gerados com dados reais validados!")