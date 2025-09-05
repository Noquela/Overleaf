# 📄 Instruções para Compilação do TCC

**Bruno Gasparini Ballerini - TCC Risk Parity**

## 🎯 SITUAÇÃO ATUAL

✅ **Todas as correções foram aplicadas:**
- Retornos logarítmicos corrigidos
- CDI com média geométrica  
- Taxa livre de risco unificada (6,195%)
- Risk Parity ERC completo
- Figura renomeada: `fluxograma_metodologia.png`

⚠️ **Necessário:** Recompilar o PDF para incluir todas as correções

---

## 🚀 OPÇÃO 1: COMPILAÇÃO LOCAL (Recomendado)

### Pré-requisitos
Instale uma distribuição LaTeX:

**Windows:**
- Baixe e instale [MiKTeX](https://miktex.org/download) OU
- Baixe e instale [TeX Live](https://tug.org/texlive/)

**Mac:**
- Instale [MacTeX](https://tug.org/mactex/)

**Linux:**
```bash
sudo apt install texlive-full    # Ubuntu/Debian
sudo yum install texlive-scheme-full  # RHEL/CentOS
```

### Compilação
Após instalar o LaTeX:

**Windows:**
```cmd
cd Overleaf\TCC_RiskParity\docs\Overleaf
compile.bat
```

**Mac/Linux:**
```bash
cd Overleaf/TCC_RiskParity/docs/Overleaf
./compile.sh
```

**Manual:**
```bash
pdflatex main.tex
bibtex main
pdflatex main.tex  
pdflatex main.tex
```

---

## 🌐 OPÇÃO 2: OVERLEAF ONLINE

1. Acesse [Overleaf.com](https://overleaf.com)
2. Crie um novo projeto
3. Upload todos os arquivos da pasta `docs/Overleaf/`:
   ```
   ├── main.tex
   ├── sections/
   │   ├── 01_capa.tex
   │   ├── 02_folha_rosto.tex
   │   ├── ...
   ├── tables/
   ├── images/
   └── fluxograma_metodologia.png
   ```
4. Clique em "Recompile"
5. Download do PDF final

---

## 🔄 OPÇÃO 3: OVERLEAF SYNC

Se você já tem projeto no Overleaf:

1. Sincronize as alterações:
   - `sections/12_metodologia.tex` (figura renomeada)
   - `fluxograma_metodologia.png` (arquivo renomeado)

2. Recompile no Overleaf

---

## ✅ VALIDAÇÃO DA COMPILAÇÃO

Após compilar, verifique:

1. **PDF gerado:** `main.pdf` (deve ter ~4-5MB)
2. **Figura do fluxograma:** Deve aparecer na Seção 3
3. **Sem erros:** LaTeX deve compilar sem erros críticos
4. **Bibliografia:** 27 referências listadas corretamente

---

## 🏆 RESULTADO ESPERADO

**PDF final com:**
- ✅ Todas as correções técnicas aplicadas
- ✅ Figura do fluxograma com nome correto
- ✅ Formatação ABNT impecável
- ✅ Bibliografia completa (27 referências)
- ✅ Pronto para a banca!

---

## 🆘 PROBLEMAS COMUNS

### Erro: "File not found: fluxograma_metodologia.png"
**Solução:** Certifique-se que o arquivo foi renomeado de `image.png` para `fluxograma_metodologia.png`

### Erro: "Package not found"
**Solução:** Instale pacotes ausentes:
```bash
# MiKTeX (Windows)
mpm --install missing-package

# TeX Live
tlmgr install missing-package
```

### Bibliografia não aparece
**Solução:** Execute bibtex:
```bash
bibtex main
pdflatex main.tex
```

---

## 📞 SUPORTE

Se tiver problemas:
1. Verifique se todos os arquivos estão no local correto
2. Use os scripts `compile.bat` ou `compile.sh`
3. Como último recurso, use o Overleaf online

**O TCC está tecnicamente pronto - só falta gerar o PDF final! 🎓**