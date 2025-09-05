#!/bin/bash
# Script de Compilacao do TCC - Bruno Gasparini Ballerini
# Executa a compilacao LaTeX completa com referencias

echo "===================================="
echo "  COMPILACAO TCC RISK PARITY"
echo "  Bruno Gasparini Ballerini"
echo "===================================="

echo
echo "[1/4] Primeira compilacao (pdflatex)..."
pdflatex -interaction=nonstopmode main.tex

echo
echo "[2/4] Processando bibliografia (bibtex)..."
bibtex main

echo
echo "[3/4] Segunda compilacao (referencias)..."
pdflatex -interaction=nonstopmode main.tex

echo
echo "[4/4] Compilacao final..."
pdflatex -interaction=nonstopmode main.tex

echo
echo "===================================="
echo "  COMPILACAO CONCLUIDA!"
echo "===================================="
echo
echo "PDF gerado: main.pdf"
echo "Tamanho: $(ls -lh main.pdf | awk '{print $5}')"

echo
echo "Limpando arquivos temporarios..."
rm -f *.aux *.log *.bbl *.blg *.toc *.lof *.lot *.out

echo
echo "PRONTO PARA A BANCA!"