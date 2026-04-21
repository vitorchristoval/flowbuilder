# FlowBuilder AI

Copiloto que converte linguagem natural em JSON válido de WhatsApp Flows, usando **RAG + LangChain + auto-correção**.

```
┌──────────────┬──────────────┬──────────────┐
│     Chat     │   Preview    │   Raw JSON   │
│  Descreva o  │  📱 Telas    │  { ... }     │
│  flow aqui   │  do flow     │  com syntax  │
│              │  visualizadas│  highlight   │
└──────────────┴──────────────┴──────────────┘
```

## Stack

| Camada | Tecnologia |
|--------|-----------|
| LLM | OpenAI GPT-4o |
| Orquestração | LangChain |
| RAG | FAISS + OpenAI Embeddings |
| Validação | Pydantic v2 |
| Backend | FastAPI |
| Frontend | Next.js 15 + Tailwind CSS v4 |

## Arquitetura

```
User Input
   ↓
Retriever (FAISS — docs + exemplos reais)
   ↓
Prompt Builder (RAG context injetado)
   ↓
LLM (GPT-4o)
   ↓
Pydantic Validator
   ↓ [inválido → até 3 tentativas de auto-correção]
JSON Final
```

---

## Rodando com Docker (recomendado)

**Pré-requisitos:** Docker instalado.

### 1. Clone o repositório

```bash
git clone <url-do-repo>
cd flowbuilder
```

### 2. Configure a chave da OpenAI

```bash
cp .env.example .env
```

Abra o `.env` e adicione sua chave:

```
OPENAI_API_KEY=sk-...
```

### 3. Suba tudo

```bash
docker compose up --build
```

Aguarde o build (primeira vez ~2 min) e acesse **http://localhost:3000**

---

## Rodando localmente (sem Docker)

**Pré-requisitos:** Python 3.12+, Node.js 20+

### Backend

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # adicione OPENAI_API_KEY
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Acesse **http://localhost:3000**

---

## Usando

1. Descreva o flow em português na tela inicial
2. Veja o preview visual e o JSON gerado
3. Peça alterações no chat — o flow anterior é preservado
4. Copie o JSON final com o botão **Copiar JSON**

### Exemplos de prompts

- *"Agendamento com nome, telefone e data"*
- *"Captura de leads com interesses"*
- *"Suporte ao cliente com tipo de problema"*
- *"Adiciona um campo de CPF no primeiro passo"*

---

## Rodando os testes

```bash
source .venv/bin/activate
pytest tests/ -v
```
