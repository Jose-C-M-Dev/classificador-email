# Classificador de Emails com IA
Sistema automatizado de classificação e resposta de emails corporativos utilizando Inteligência Artificial e técnicas de Processamento de Linguagem Natural (NLP).

site: https://autoemail-d7ni.onrender.com
___
##  Sobre o Projeto
Classifica emails em categorias (Produtivo/Improdutivo)\
Sugere respostas automáticas baseadas na classificação\
Processa múltiplos arquivos simultaneamente (txt, pdf)\
Aplica técnicas de NLP para pré-processamento de texto\
Demonstra ajuste de modelo através de validação e métricas
___
## Tecnologias Utilizadas

- **Backend**

**Python 3.10+**\
**FastAPI** - Framework web moderno e rápido\
**Groq API** - LLM para classificação e geração de respostas\
**NLTK** - Processamento de linguagem natural\
**PyPDF2** - Extração de texto de PDFs\
**Httpx** - Cliente HTTP assíncrono


- **Frontend**

HTML5 / CSS3 / JavaScript vanilla\
Design responsivo com grid layout\
Drag & Drop para upload de arquivos
___
## Estrutura do Projeto

```plaintext
email-classifier/
│
├── app/
│   ├── __init__.py
│   ├── main.py              # Rotas FastAPI
│   ├── models.py            # Modelos Pydantic
│   ├── ai_service.py        # Integração com LLM + NLP
│   ├── file_processor.py    # Extração de texto
│   ├── prompts.py           # Prompts com few-shot learning
│   ├── nlp_processor.py     # Pipeline NLP completo
│   └── ai_validator.py      # Validação e métricas
│
├── static/
│   ├── index.html           # Interface web
│   ├── style.css            # Estilos
│   └── script.js            # Lógica frontend
│
├── .env                     # Variáveis de ambiente (criar)
├── .env.example             # Exemplo de configuração
├── requirements.txt         # Dependências Python
└── README.md               # Este arquivo
```
___
## Funcionalidades

**1. Processamento de Emails**

- Upload de múltiplos arquivos (.txt, .pdf)
- Inserção direta de texto
- Drag & drop intuitivo
- Limite de 10 arquivos por processamento

**2. Classificação Inteligente**

- Categoria Produtivo: Requer ação (reuniões, prazos, suporte, etc.)
- Categoria Improdutivo: Não requer ação (saudações, agradecimentos, spam)
- Nível de confiança (0-100%)
- Justificativa da classificação

**3. Processamento NLP**

- Limpeza de texto: Remoção de URLs, emails, telefones
- Tokenização: Separação em palavras individuais
- Remoção de stopwords: Eliminação de palavras irrelevantes (português)
- Stemming: Redução de palavras à raiz (RSLP)
- Extração de keywords: Identificação das palavras-chave mais relevantes
- Normalização: Conversão para minúsculas e remoção de acentos

**4. Interface Avançada**

- Estatísticas em tempo real (atual + histórico)
- Filtros por categoria
- Histórico paginado (5 por página)
- Expansão de detalhes
- Design moderno com gradientes

**5. Ajuste e Validação do Modelo**

- Few-shot learning: Exemplos no prompt para melhorar classificação
- Conjunto de validação: 5 casos de teste pré-definidos
- Métricas de performance: Acurácia, precisão, recall, F1-score
- Matriz de confusão: TP, FP, TN, FN
- Ajuste dinâmico: Temperatura e max_tokens variam por categoria
---
#  Utilização

**Pré-requisitos**
```plaintext
Python 3.10 ou superior
pip (gerenciador de pacotes Python)
```
**Clone o repositório**
```plaintext
git clone https://github.com/seu-usuario/email-classifier.git
cd email-classifier
```
**Crie ambiente virtual**
```plaintext
python -m venv venv
venv\Scripts\activate
```
**Instale dependências**
```plaintext
pip install -r requirements.txt
```
**Groq** 
```plaintext
Acesse: https://console.groq.com
Faça login/cadastro
Navegue até API Keys
Gere uma nova chave
```
**Download de recursos NLTK**
```plaintext
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('rslp')"
```
**Execute a aplicação**
```plaintext
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Acesse: http://localhost:8000
___
## Validação do Modelo (Demonstração de Ajuste)
```plaintext
python -m app.ai_validator
```
Saída esperada:
```plaintext
============================================================
VALIDAÇÃO DO MODELO DE CLASSIFICAÇÃO DE EMAILS
============================================================

   MÉTRICAS DE PERFORMANCE:
   Total de exemplos testados: 5
   Classificações corretas: 5
   Classificações incorretas: 0
   Acurácia: 100.0%
   Precisão: 100.0%
   Recall: 100.0%
   F1-Score: 100.0%

   MATRIZ DE CONFUSÃO:
   Verdadeiros Positivos (TP): 3
   Falsos Positivos (FP): 0
   Verdadeiros Negativos (TN): 2
   Falsos Negativos (FN): 0
```
Este processo demonstra:

1. Validação cruzada com casos conhecidos\
2. Cálculo de métricas de desempenho\
3. Identificação de erros para ajuste\
4. Recomendações automáticas de melhoria
___
# Scripts Úteis
**Testar classificação individual**
```plaintext
python -c "from app.ai_service import classify_one; import asyncio; print(asyncio.run(classify_one('Seu texto aqui')))"
```
**Executar validação completa**
```plaintext
python -m app.ai_validator
```
**Testar preprocessamento NLP**
```plaintext
python -c "from app.nlp_processor import preprocess_email; import json; print(json.dumps(preprocess_email('Seu texto aqui'), indent=2, ensure_ascii=False))"
```
