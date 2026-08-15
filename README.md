🚗 Sistema Inteligente de Detecção de Vagas de Estacionamento
═════════════════════════════════════════════════════════════

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenCV 4.5+](https://img.shields.io/badge/opencv-4.5+-brightgreen.svg)](https://opencv.org)
[![Flask 2.0+](https://img.shields.io/badge/flask-2.0+-red.svg)](https://flask.palletsprojects.com)
[![Status: Ativo](https://img.shields.io/badge/status-ativo-success.svg)]()

**Trabalho de Conclusão de Curso | Faculdade Una Campus Divinópolis | 2025**

---

## 📌 O Que é Este Projeto?

Sistema inteligente que utiliza **visão computacional** para detectar automaticamente quais vagas de estacionamento estão ocupadas ou livres em **tempo real**. 

Desenvolvido em **Python** com **OpenCV**, **Flask** e **NumPy**, este projeto foi **validado em uma maquete funcional com 4 vagas** para garantir a precisão e confiabilidade do sistema.

---

## ⭐ Principais Características

✅ **Detecção em Tempo Real**  
   - Processa 30 FPS com <100ms latência
   - >95% acurácia em ambiente controlado

✅ **Validação Prática em Maquete**  
   - Maquete funcional com 4 vagas em linha
   - Câmera HD 1280×720 pixels
   - Iluminação uniforme e calibração interativa
   - 5 fases de teste documentadas

✅ **3 Versões do Código**  
   - **V1**: Protótipo inicial para validação conceitual
   - **V2**: Sistema desktop robusto com câmera USB ao vivo
   - **V3**: Aplicação web profissional com dashboard interativo

✅ **Calibração Intuitiva**  
   - Clique em 2 pontos por vaga para calibração automática
   - Threshold adaptativo que se ajusta à iluminação

✅ **Reconexão Automática de Câmera**  
   - Detecta desconexão e reconecta automaticamente
   - Sem perda de funcionalidade

✅ **Interface Web Profissional**  
   - Dashboard com sidebar com métricas
   - Stream de vídeo em tempo real
   - Sliders interativos para ajuste de threshold
   - Responsivo em desktop, tablet e mobile

---

## 🏢 Maquete - Validação Prática

Este projeto foi desenvolvido e **validado em uma maquete funcional** que simula um cenário real de estacionamento:

### 📐 Especificações da Maquete

| Aspecto | Detalhes |
|---------|----------|
| **Vagas** | 4 vagas funcionais em linha |
| **Dimensões** | 42cm (comprimento) × 30cm (profundidade) |
| **Câmera** | 1280×720 pixels (HD) - Ângulo 30-45° |
| **Iluminação** | LED branca uniforme (500-800 lux) |
| **Material** | Papelão resistente |
| **Calibração** | Interativa por clique (2 pontos por vaga) |

### ✅ 5 Fases de Teste Realizadas

1. **Validação Visual** → Detecção correta com cores dos retângulos
2. **Vagas Vazias** → 4/4 livres com retângulos verdes ✓
3. **Ocupação Progressiva** → 0→1→2→3→4 vagas ocupadas ✓
4. **Sensibilidade de Threshold** → Ótimo em 2500-3500 pixels ✓
5. **Calibração Dinâmica** → Clique interativo funcional ✓

### 📊 Resultados Comprovados

- **Taxa de Detecção**: >95% acurácia
- **Falsos Positivos**: <2%
- **Falsos Negativos**: <2%
- **Performance**: <100ms por frame (30 FPS)
- **Status**: ✅ **TODAS 5 FASES APROVADAS**

## 🛠️ Tecnologias Utilizadas

### 🐍 Linguagem de Programação
- **Python 3.8+** - Linguagem principal

### 👁️ Visão Computacional
- **OpenCV 4.5+** - Captura, processamento, threshold adaptativo, streaming MJPEG

### 🌐 Web Framework
- **Flask 2.0+** - Servidor web, API REST, rotas HTTP

### 📊 Computação Numérica
- **NumPy 1.20+** - Operações matemáticas, manipulação de arrays

### ⚙️ Processamento
- **Threading** - Processamento paralelo e sincronização

### 💻 Frontend
- **HTML/CSS/JavaScript** - Interface web interativa

### 📹 Hardware Recomendado
- Câmera USB 1280×720 pixels
- CPU Intel i5 / AMD Ryzen 5
- RAM: 4GB mínimo
- Windows 10/11, Linux (Ubuntu 20.04+) ou macOS 10.14+

---

## 📁 Estrutura do Repositório

```
Estacionamento-Inteligente-TCC/
│
├── 📄 README.md                          ← Você está aqui!
├── 📄 LICENSE                            ← MIT License
├── 📄 requirements.txt                   ← Dependências Python
├── 📄 .gitignore                         ← Arquivos a ignorar
├── 📄 CONTRIBUTORS.md                    ← Lista de integrantes
│
├── 📂 src/                               ← CÓDIGO-FONTE (2 versões principais)
│   ├── 📂 v2_sistema_local/
│   │   └── 🐍 Estacionamento_Final.py   ← V2: Desktop com câmera ao vivo
│   │
│   └── 📂 v3_sistema_web/
│       ├── 🐍 Estacionamento_FLASK_Final.py
│       ├── 📂 templates/
│       │   └── 📄 index.html            ← Interface web
│       ├── 📂 static/
│       │   ├── 📄 style.css             ← Estilos
│       │   └── 📄 script.js             ← Interatividade
│       └── 📄 requirements.txt           ← Dependências V3
│
├── 📂 docs/                              ← DOCUMENTAÇÃO
│   ├── 📄 INSTALACAO.md                 ← Guia de instalação
│   ├── 📄 GUIA_USO.md                   ← Como usar cada versão
│   ├── 📄 ARQUITETURA.md                ← Diagrama e arquitetura
│   └── 📄 ESPECIFICACOES_TECNICAS.md    ← Detalhes técnicos
│
├── 📂 maquete/                           ← MAQUETE E TESTES ⭐
│   ├── 📄 ESPECIFICACOES_MAQUETE.md    ← Specs técnicas da maquete
│   ├── 📄 TESTES_REALIZADOS.md          ← Resultados das 5 fases
│   ├── 📄 CALIBRACAO.md                 ← Como calibrar
│   └── 📂 FOTOS_MAQUETE/                ← Imagens do protótipo
│
├── 📂 apresentacao/                      ← APRESENTAÇÃO INTERATIVA
│   └── 📄 index.html                    ← Slides profissionais (12 slides)
│
└── 📂 referencias/                       ← MATERIAIS DE REFERÊNCIA
    ├── 📄 opencv_documentation.pdf
    ├── 📄 flask_best_practices.pdf
    └── 📂 computer_vision_papers/
```

---

## 🚀 Quick Start (5 Minutos!)

### ⬇️ 1. Clonar o Repositório

```bash
git clone https://github.com/seu-usuario/Estacionamento-Inteligente-TCC.git
cd Estacionamento-Inteligente-TCC
```

### 📦 2. Instalar Dependências

```bash
# Criar ambiente virtual (recomendado)
python -m venv venv

# Ativar ambiente virtual
# No Windows:
venv\Scripts\activate
# No Linux/Mac:
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### ▶️ 3. Executar uma das Versões

#### 🖥️ **Versão 2: Sistema Desktop (Com Câmera)**

```bash
cd src/v2_sistema_local
python Estacionamento_Final.py
```

**Controles:**
| Tecla | Ação |
|-------|------|
| **P** | Pausar/Retomar |
| **M** | Modo Normal/Threshold |
| **C** | Calibrar |
| **F** | Finalizar calibração |
| **+/-** | Ajustar threshold |
| **1-4** | Selecionar vaga |
| **Q** | Sair |

#### 🌐 **Versão 3: Sistema Web (Flask)**

```bash
cd src/v3_sistema_web
python Estacionamento_FLASK_Final.py

# Abrir no navegador:
# http://localhost:5000
```

**Funcionalidades:**
- 📊 Dashboard interativo com métricas
- 📹 Stream de vídeo em tempo real
- 🎚️ Sliders para ajuste de threshold de cada vaga
- 🔴 Status visual (🟢 Livre | 🔴 Ocupada)
- 🔄 Reconexão automática de câmera

---

## 📖 Como Usar Cada Versão

### 🔴 Versão 1: Protótipo Inicial (tstfabin.py)
**Status:** Validação conceitual  
**Uso:** Apenas para entender o conceito básico  
**Limitações:** Não usa câmera ao vivo, entrada de vídeo estática

### 🟡 Versão 2: Sistema Desktop (Estacionamento_Final.py)
**Status:** Pronto para ambiente controlado (maquete)  
**Uso:** Executar em seu computador com câmera USB  
**Vantagens:**
- Câmera USB ao vivo ✓
- 4 vagas configuráveis ✓
- Calibração interativa ✓
- Threshold ajustável ±200 pixels ✓
- 10+ controles por teclado ✓
- **Testado e validado em maquete** ✓

### 🟢 Versão 3: Sistema Web (Estacionamento_FLASK_Final.py)
**Status:** Pronto para produção em pequenos/médios estacionamentos  
**Uso:** Acesso via navegador web  
**Vantagens:**
- Interface profissional em dashboard ✓
- Acesso remoto via navegador ✓
- Sliders interativos em tempo real ✓
- API REST completa (10+ rotas) ✓
- Stream MJPEG de vídeo ✓
- Reconexão automática ✓
- **Também testado em maquete** ✓

---

## 📊 Resultados e Estatísticas

### Desempenho na Maquete

```
Acurácia de Detecção:     ████████████████████ 95%+
Falsos Positivos:         ██░░░░░░░░░░░░░░░░░░ <2%
Falsos Negativos:         ██░░░░░░░░░░░░░░░░░░ <2%
Performance (FPS):        ████████████████████ 30 FPS
Latência por Frame:       ████░░░░░░░░░░░░░░░░ <100ms
```

### Validação Técnica

✅ **Threshold Adaptativo**  
   - Fórmula: T(x,y) = 255 se pixel > (média - 16)
   - Adapta-se automaticamente a variações de iluminação

✅ **Processamento de Pipeline**  
   1. Captura frame (BGR 1280×720)
   2. Conversão escala cinza
   3. Threshold adaptativo gaussiano
   4. Median blur (suavização)
   5. Dilatação morfológica
   6. Extração ROI por vaga
   7. Contagem de pixels brancos
   8. Comparação com threshold
   9. Classificação (Ocupada/Livre)
   10. Desenho de retângulos
   11. Codificação JPEG → MJPEG

✅ **Reconexão Automática de Câmera**  
   - Detecta desconexão
   - Reconecta automaticamente
   - Sem perda de dados

---

## 🎯 Viabilidade

### ✅ Recomendado Para

- Estacionamentos pequenos/médios (4-8 vagas)
- Ambientes com iluminação controlada
- Prototipagem e testes
- Ambientes acadêmicos

### ⚠️ Limitações

- Até 50 usuários simultâneos (V3)
- Requer iluminação uniforme
- Não recomendado para grandes estacionamentos sem otimizações extras

---

## 🔮 Futuras Melhorias

- [ ] Integração com aplicativo mobile (React Native/Flutter)
- [ ] Machine Learning para otimização de detecção
- [ ] Suporte para múltiplas câmeras
- [ ] Integração com sistema de pagamento
- [ ] Dashboard administrativo com relatórios
- [ ] Banco de dados para análise histórica
- [ ] Notificações push em tempo real
- [ ] API pública para integrações externas

---

## 📚 Referências Bibliográficas

[1] OpenCV: Open Source Computer Vision Library  
[2] Flask Web Development - Miguel Grinberg  
[3] NumPy: Fundamental Package for Scientific Computing  
[4] Python 3 Official Documentation  
[5] Bradski, G. & Kaehler, A. (2008). *Learning OpenCV*  
[6] Szeliski, R. (2010). *Computer Vision: Algorithms and Applications*  
[7] Gonzalez, R. C. & Woods, R. E. (2008). *Digital Image Processing*  
[8] Various Computer Vision Research Papers  

---

## 📄 Licença

Este projeto está licenciado sob a **MIT License** - veja arquivo [`LICENSE`](LICENSE) para detalhes.

**Em resumo:** Você pode usar, modificar e distribuir este código livremente, desde que inclua a licença original.

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Se deseja contribuir:

1. Faça um **fork** do repositório
2. Crie uma **branch** para sua feature (`git checkout -b feature/MeuImprovement`)
3. **Commit** suas mudanças (`git commit -m 'Adiciona meu improvement'`)
4. **Push** para a branch (`git push origin feature/MeuImprovement`)
5. Abra um **Pull Request**

---

## 💬 Suporte e Dúvidas

Encontrou um problema ou tem dúvidas?

- 🐛 Abra uma **Issue** no repositório
- 💬 Deixe um comentário na **Discussion**
- 📧 Entre em contato conosco

---

## 🎓 Contexto Acadêmico

**Instituição:** Faculdade Una Campus Divinópolis  
**Curso:** Ciência da Computação  
**Tipo:** Trabalho de Conclusão de Curso (TCC)  
**Ano:** 2025  
**Bimestre:** 2º Bimestre  
**Projeto:** A3 - Projeto Integrado  

Este projeto demonstra a aplicação prática de conceitos de:
- 👁️ Visão Computacional
- 🐍 Python Profissional
- 🌐 Desenvolvimento Web
- ⚙️ Engenharia de Software
- 🧪 Testes e Validação

---

## 🏆 Destaques

🎯 **Projeto Prático e Validado**  
- Não é apenas teoria! Sistema testado em maquete funcional com resultados comprovados

💡 **3 Níveis de Implementação**  
- Protótipo → Desktop → Web. Aprenda vendo a evolução do projeto

🔬 **Documentação Acadêmica**  
- Completa em formato ABNT com referências bibliográficas

🚀 **Pronto para Produção**  
- V3 é utilizável em cenários reais (pequenos/médios estacionamentos)

---

## 📊 Estatísticas do Projeto

- **Linhas de Código:** ~2000+ linhas
- **Versões:** 3 versões principais
- **Documentação:** 10+ arquivos
- **Tempo de Desenvolvimento:** Semestral
- **Validação Prática:** ✅ Maquete com 4 vagas
- **Taxa de Sucesso:** >95% acurácia
- **Integrantes:** 5 desenvolvedores

---

## 🎉 Conclusão

Este é um projeto completo que vai da **teoria à prática**, passando por **prototipagem**, **validação em ambiente simulado** e **implementação web**. 

Idealmente, você pode:
1. Estudar o código como exemplo de boas práticas
2. Rodá-lo na sua máquina com webcam
3. Adaptá-lo para seus próprios casos de uso
4. Usar como base para pesquisas futuras

**Qualquer dúvida ou sugestão, abra uma issue!** 🚀

---

**Desenvolvido com ❤️ por**  
Brunno Korps • João Pedro • Luiz Otávio • Pedro Medeiros • Rafael Jacinto

*Faculdade Una Campus Divinópolis | 2025*
