# FlowBuilder AI

> Copiloto que converte linguagem natural em JSON válido de WhatsApp Flows — eliminando a dependência de desenvolvedor para PMs, CS e marketing.

```
┌──────────────┬──────────────┬──────────────┐
│     Chat     │   Preview    │   Raw JSON   │
│  Descreva o  │  📱 Telas    │  { ... }     │
│  flow aqui   │  do flow     │  com syntax  │
│              │  visualizadas│  highlight   │
└──────────────┴──────────────┴──────────────┘
```

---

## 1. Definição do Problema e Público

### O problema

WhatsApp Flows é o recurso da Meta que permite inserir formulários multi-tela — com lógica condicional e data exchange — dentro do WhatsApp: checkout, qualificação de lead, agendamento, onboarding, KYC, NPS.

Criar um Flow exige escrever um **FlowJSON** seguindo a spec da Meta: ~15 tipos de componentes, regras de navegação entre telas, `on-click-action`, versão de schema, payloads de data exchange. Hoje, **é tarefa de desenvolvedor**.

### Quem sofre

| Perfil | Dor |
|--------|-----|
| **PMs, CS e marketing** em empresas que usam WhatsApp como canal | Dependem do time de engenharia para qualquer alteração — mesmo trocar uma pergunta ou adicionar uma opção |
| **PMEs** sem time de dev | Simplesmente desistem de Flows, caindo em experiências inferiores (listas, botões, conversas longas) |

### Impacto hoje

- Um Flow simples (2 telas, 4–5 campos) leva **2–4h de dev**; Flows com ramificação e data exchange passam de **1–2 dias**
- Desenvolvedor vira caminho crítico de campanhas: time-to-market que deveria ser horas vira semanas
- Erros de schema geram rejeição no publish da Meta e retrabalho
- A/B testar variações de Flow é inviável na prática

---

## 2. Solução

### Como o FlowBuilder AI resolve

O copiloto transforma uma descrição em linguagem natural em um FlowJSON pronto para publicar na Meta, em menos de 1 minuto, sem nenhum conhecimento técnico.

**Pipeline:**

```
Descrição do usuário
       ↓
  Retriever RAG
  (FAISS + spec + exemplos reais)
       ↓
  Prompt Builder
  (contexto injetado)
       ↓
  GPT-4o
       ↓
  Pydantic Validator
  (schema v7.2)
       ↓ [inválido → até 3 tentativas de auto-correção]
  JSON final válido
```

**Diferenciais:**

- **RAG sobre a spec real da Meta** — o modelo nunca alucina componentes inexistentes
- **Auto-correção com loop de validação** — erros de schema são detectados e corrigidos automaticamente sem intervenção do usuário
- **Contexto conversacional** — o usuário pode pedir alterações ("adiciona campo de CPF") e o flow anterior é preservado
- **Preview visual** — cada tela renderizada como mockup de celular antes de publicar

---

## 3. Plano de Validação

### Hipótese principal

> "Usuários não-técnicos (PM, CS, marketing) conseguem criar Flows prontos para produção usando linguagem natural, reduzindo o tempo de publicação de horas/dias para minutos e eliminando dependência de desenvolvedor em ≥70% dos casos de uso."

### Sub-hipóteses

| ID | Hipótese | Critério |
|----|----------|----------|
| H1 | Qualidade do output | ≥85% dos Flows gerados passam na validação da Meta na primeira tentativa |
| H2 | Cobertura | Cobre os 5–7 arquétipos de maior uso real (lead gen, agendamento, NPS, cadastro, checkout, KYC, pesquisa) |
| H3 | Confiança do usuário | O não-técnico se sente confortável em publicar sem revisão de dev |
| H4 | Iteração conversacional | Refinar o Flow no chat é mais rápido que editar JSON manualmente |

### Cronograma de 1 semana

| Dia | Ação |
|-----|------|
| **1** | Recrutamento de 6–8 participantes (PM/PO, CS/ops, marketing). Critério: já tentou criar/ajustar um Flow ou evitou por barreira técnica |
| **2–3** | Sessões de usabilidade moderada (45 min gravadas): (a) criar Flow a partir de briefing; (b) modificar Flow existente |
| **3–5** | Uso não-moderado com acesso livre; telemetria captura tudo; pede-se publicação em sandbox |
| **6** | Entrevistas de saída (20 min): SUS, NPS, "pagaria por isso?", "o que faltou?" |
| **7** | Síntese — cruzar quantitativo com qualitativo; definir go/no-go |

### Critérios de decisão

- 🟢 **Verde:** ≥70% completam ambas as tarefas sem ajuda; SUS >75; ≥4/6 usariam semanalmente; ≥3/6 demonstram disposição a pagar
- 🟡 **Amarelo:** completam com ajuda moderada mas ficam inseguros em publicar → roadmap de explicabilidade e preview
- 🔴 **Vermelho:** taxa de Flow válido <60% ou usuários voltam a pedir "só um dev dar uma olhada"

---

## 4. KPIs de Sucesso

### Técnicos — o motor funciona

| KPI | Meta |
|-----|------|
| Taxa de JSON válido contra schema FlowJSON | ≥ 90% |
| Taxa de sucesso na primeira tentativa (sem iteração) | ≥ 70% |
| Taxa de auto-correção após erro de validação | ≥ 80% |
| Número médio de turnos até o Flow final | < 3 |
| Latência p95 para Flows de até 3 telas | < 10s |
| Taxa de alucinação de componente | < 2% |

### Produto / UX

| KPI | Meta |
|-----|------|
| Tempo da intenção ao Flow publicado | < 15 min (baseline: ~4h com dev) |
| Task completion rate nas tarefas de teste | ≥ 85% |
| Flows criados por usuário ativo por semana | — (baseline a definir) |

### Negócio — isso vale?

| KPI | Meta |
|-----|------|
| Flows publicados por cliente/mês | ↑ vs. coorte sem copiloto |
| Activation rate do feature Flows na base | ↑ vs. baseline |
| NPS do feature | ≥ 40 |
| % clientes que aumentam volume de campanhas via Flow após adoção | proxy de receita adicional |

---

## 5. Decisões Técnicas e Trade-offs

### Por que RAG em vez de fine-tuning?

A spec do WhatsApp Flows muda com frequência. RAG permite atualizar a base de conhecimento adicionando arquivos em `knowledge/` sem retreinar nada. Fine-tuning "congela" o conhecimento e exige reprocessamento a cada versão.

### Por que FAISS em vez de Pinecone/Weaviate?

Para um MVP/desafio técnico, FAISS roda localmente sem dependência de serviço externo, sem custo e sem latência de rede. O trade-off é que não escala horizontalmente — para produção, a migração para Chroma ou Pinecone é direta via interface do LangChain.

### Por que validação Pydantic + loop de correção?

LLMs erram. A validação determinística com Pydantic garante que nenhum JSON inválido chegue ao usuário. O loop de auto-correção (até 3 tentativas) transforma o erro de validação em contexto para o próximo prompt — o modelo lê o próprio erro e corrige. Na prática, ≥95% dos casos resolvem em 1–2 tentativas.

### Por que Next.js separado em vez de servir o frontend pelo FastAPI?

Separação de responsabilidades e DX: o backend foca em API, o frontend tem hot-reload independente. Em produção, o Next.js pode ser deployado na Vercel e o FastAPI em qualquer container. O trade-off é ter dois processos para rodar localmente — resolvido pelo Docker Compose.

### Trade-offs assumidos

| Decisão | Ganho | Custo |
|---------|-------|-------|
| GPT-4o como único LLM | Qualidade máxima de output | Custo por token mais alto; dependência de fornecedor |
| FAISS local | Zero infra, zero custo | Não escala horizontalmente; índice in-memory |
| Schema Pydantic permissivo (`extra: allow`) | Flexibilidade para campos futuros da Meta | Validação menos estrita — campos desconhecidos passam sem erro |
| Auto-correção síncrona | Simples de implementar e debugar | Adiciona latência em caso de erro; até 3x o custo de tokens por Flow |

---

## 6. Stack Técnica

| Camada | Tecnologia |
|--------|-----------|
| LLM | OpenAI GPT-4o |
| Orquestração | LangChain |
| RAG | FAISS + OpenAI Embeddings (text-embedding-3-small) |
| Validação | Pydantic v2 |
| Backend | FastAPI + Uvicorn |
| Frontend | Next.js 15 + Tailwind CSS v4 |
| Integração externa | OpenAI API + filesystem (base de conhecimento) |

---

## 7. Como Rodar

### Com Docker (recomendado)

**Pré-requisito:** Docker instalado.

```bash
# 1. Clone
git clone <url-do-repo>
cd flowbuilder

# 2. Configure a chave
cp .env.example .env
# edite .env e adicione: OPENAI_API_KEY=sk-...

# 3. Suba tudo
docker compose up --build
```

Acesse **http://localhost:3000**

---

### Sem Docker

**Backend**

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # adicione OPENAI_API_KEY
uvicorn app.main:app --reload
```

**Frontend** (outro terminal)

```bash
cd frontend
npm install
npm run dev
```

Acesse **http://localhost:3000**

---

### Testes

```bash
source .venv/bin/activate
pytest tests/ -v
```

---

## 8. Expandindo a Base de Conhecimento

Adicione arquivos `.json` em:

- `knowledge/docs/` — documentação de componentes
- `knowledge/examples/` — exemplos reais de Flows

O índice RAG é reconstruído automaticamente na próxima inicialização do backend.
