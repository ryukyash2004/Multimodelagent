# AGENT.md

> **Student:** AI IDE / AI Engineering Student
> **Project:** Atlas — Enterprise Multimodal AI Assistant Platform
> **Purpose:** A self-guided, progressive learning agent. You (the student) attempt every step FIRST. Help is layered — notes → questions → hints → approach → **last resort: full answer**.

---

## 📜 How This File Works (Read Me First)

This is your **learning contract**. At every step you must attempt the work yourself before unlocking help.

### Help Ladder (always follow this order)
1. **📘 Notes** — Background concepts you should understand.
2. **❓ Questions** — Socratic prompts to make you think. Answer them in your own words *before* reading further.
3. **💡 Hints** — Gentle nudges, not solutions.
4. **🧭 Approach** — The *what & why* of the solution (no code).
5. **🆘 Answer (LAST RESORT)** — Full solution, only after you've tried everything above. **You must write one line: `"I tried and here's what I learned"` before reading it.**

### Rules for the Student (You)
- [ ] Never open **🆘 Answer** first. It defeats the purpose.
- [ ] Write your attempt in a `NOTES.md` file per step.
- [ ] If stuck >30 minutes, move one rung down the ladder.
- [ ] After finishing, explain the step aloud as if teaching a junior — if you can't, redo it.

### Rules for the AI (Assistant role)
- When the student asks for help, **always start at 📘 Notes** unless they specify a rung.
- Never jump to 🆘 unless the student explicitly types: `GIVE ME THE ANSWER`.
- Ask the ❓ Questions back to the student and wait for their response.
- Mark each step as `[ ] pending`, `[/] in progress`, `[x] done`.

---

## 🎯 Project Roadmap (High-Level)

```
PHASE 1 — Local RAG Foundation
PHASE 2 — Agentic Orchestration
PHASE 3 — Workspace Connectors (OAuth)
PHASE 4 — Multimodal Inputs
PHASE 5 — Serverless Cloud Deploy
PHASE 6 — Enterprise Governance
PHASE 7 — Evaluation & Demo
```

Each phase below follows the same template: **Notes → Questions → Hints → Approach → Answer**.

---

# 🟩 PHASE 1 — Local RAG Foundation

## Step 1.1 — Environment Setup

**Status:** `[x] agent works`

### 📘 Notes
- A **virtual environment** isolates Python packages per project so versions don't collide.
- **Ollama** runs LLMs locally (no API cost, good for learning).
- You need: Python 3.11+, `pip`, `git`, and Ollama installed.

### ❓ Questions
1. Why is a virtual environment important when you'll later deploy to Cloud Run?
2. What's the difference between a *model* and an *embedding model*?

### 💡 Hints
- Consider `uv` or `poetry` instead of plain `venv` — modern, faster.
- Test Ollama with `ollama run gemma3:4b` before writing any Python.

### 🧭 Approach
Create a project folder, initialize `git`, create a virtualenv, install `langchain`, `langchain-community`, `chromadb`, `pypdf`, and pull two Ollama models: one chat model, one embedding model.

### 🆘 Answer (LAST RESORT)
```bash
mkdir atlas && cd atlas
git init
python -m venv .venv && source .venv/bin/activate
pip install langchain langchain-community chromadb pypdf ollama
ollama pull gemma3:4b
ollama pull nomic-embed-text
echo ".venv/" > .gitignore
```
Write a `hello_rag.py` that asks Ollama "What is RAG?" and prints the response.

---

## Step 1.2 — Build a Naive RAG Pipeline

**Status:** `[ ] pending`

### 📘 Notes
- RAG = **Retrieve** relevant text → **Augment** the prompt → **Generate** answer.
- Core steps: **load → split → embed → store → retrieve → generate**.

### ❓ Questions
1. What happens if you split documents into chunks that are too small? Too large?
2. Why do we retrieve *before* generating instead of just asking the LLM directly?

### 💡 Hints
- Start with **one PDF** (a public annual report).
- `RecursiveCharacterTextSplitter` with `chunk_size=800, overlap=100` is a sane default.
- Print the retrieved chunks *before* sending them to the LLM — debug visually.

### 🧭 Approach
Write a script that:
1. Loads a PDF with `PyPDFLoader`.
2. Splits with `RecursiveCharacterTextSplitter`.
3. Embeds via Ollama's `nomic-embed-text` into Chroma.
4. Creates a retriever (`k=3`).
5. Builds a prompt template: `Answer using only this context: {context}. Question: {question}`.
6. Prints the answer + the sources.

### 🆘 Answer (LAST RESORT)
```python
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

docs = PyPDFLoader("report.pdf").load()
chunks = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100).split_documents(docs)

emb = OllamaEmbeddings(model="nomic-embed-text")
vs = Chroma.from_documents(chunks, emb)
retriever = vs.as_retriever(search_kwargs={"k": 3})

prompt = ChatPromptTemplate.from_template(
    "Answer only from context.\nContext: {context}\nQuestion: {question}"
)
llm = ChatOllama(model="gemma3:4b")
chain = {"context": retriever, "question": RunnablePassthrough()} | prompt | llm

print(chain.invoke("What was the revenue growth?").content)
```

---

## Step 1.3 — Evaluate Your RAG (RAGAS)

**Status:** `[ ] pending`

### 📘 Notes
- You cannot improve what you don't measure. **RAGAS** scores faithfulness, answer relevancy, context precision/recall.
- You need a small **golden dataset**: ~10 Q&A pairs with correct answers.

### ❓ Questions
1. What does "faithfulness" mean, and why does it matter more than "sounds right"?
2. If context recall is low, what part of your pipeline is broken?

### 💡 Hints
- Write 10 questions whose answers you already know exist in the PDF.
- Install: `pip install ragas datasets`.

### 🧭 Approach
Create `eval/golden.json` with questions + ground truths. Run RAGAS with your chain wrapped as a callable. Log the four metrics to a CSV and iterate on chunk size until scores improve.

### 🆘 Answer (LAST RESORT)
```python
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
from datasets import Dataset

data = {
    "question": ["What was revenue growth?"],
    "answer": [chain.invoke("What was revenue growth?").content],
    "contexts": [[d.page_content for d in retriever.invoke("What was revenue growth?")]],
    "ground_truth": ["Revenue grew 12% YoY."],
}
result = evaluate(Dataset.from_dict(data),
                  metrics=[faithfulness, answer_relevancy, context_precision, context_recall])
print(result)
```
Iterate `chunk_size` ∈ {400, 800, 1200} and keep the best.

---

# 🟦 PHASE 2 — Agentic Orchestration

## Step 2.1 — Your First LangGraph Agent

**Status:** `[ ] pending`

### 📘 Notes
- **LangGraph** models agents as a **state machine**: nodes (functions) + edges (transitions).
- State is a shared dict passed between nodes. Common pattern: `{"messages": [...]}`.
- A **router** decides which node runs next.

### ❓ Questions
1. When would a *graph* beat a simple sequential chain?
2. Why is explicit state better than relying on a chain's implicit memory?

### 💡 Hints
- Install: `pip install langgraph`.
- Start with **two nodes**: `rag_search` and `direct_answer`.
- Use `StateGraph(TypedDict)` and `add_conditional_edges`.

### 🧭 Approach
Build a graph:
- **Node A — classify**: LLM returns `"rag"` or `"chat"`.
- **Node B — rag_search**: runs your Step 1.2 chain.
- **Node C — direct_answer**: answers without context.
- **Conditional edge** from A routes to B or C based on the classification.
- **END** after B or C.

### 🆘 Answer (LAST RESORT)
```python
from typing import TypedDict
from langgraph.graph import StateGraph, END

class S(TypedDict):
    messages: list
    route: str

def classify(state: S) -> S:
    q = state["messages"][-1]
    route = "rag" if "document" in q.lower() else "chat"
    return {"route": route}

def rag_node(state: S) -> S:
    ans = chain.invoke(state["messages"][-1]).content
    return {"messages": state["messages"] + [ans]}

def chat_node(state: S) -> S:
    ans = llm.invoke(state["messages"][-1]).content
    return {"messages": state["messages"] + [ans]}

g = StateGraph(S)
g.add_node("classify", classify)
g.add_node("rag", rag_node)
g.add_node("chat", chat_node)
g.set_entry_point("classify")
g.add_conditional_edges("classify", lambda s: s["route"], {"rag": "rag", "chat": "chat"})
g.add_edge("rag", END); g.add_edge("chat", END)
app = g.compile()
print(app.invoke({"messages": ["Tell me about revenue from the document"]}))
```

---

## Step 2.2 — Add Tool Calling

**Status:** `[ ] pending`

### 📘 Notes
- **Tools** are functions the LLM can *choose* to call. The LLM outputs a structured call; your code executes it.
- In LangGraph/LangChain, decorate with `@tool` and bind with `llm.bind_tools([...])`.

### ❓ Questions
1. What's the security risk of letting an LLM call arbitrary tools?
2. How does the agent know when it's "done" and should return to the user?

### 💡 Hints
- Define simple tools first: `add(a, b)`, `get_current_time()`.
- Use `ToolNode` from `langgraph.prebuilt`.
- Add a `tools_condition` edge to loop until no tool call is requested.

### 🧭 Approach
Wrap your RAG retriever as a `@tool def search_docs(query: str)`. Bind it to the LLM. Build a graph: `agent → (tools?) → back to agent → END`. Test with "Search the docs for revenue" and confirm the tool fires.

### 🆘 Answer (LAST RESORT)
```python
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition

@tool
def search_docs(query: str) -> str:
    """Search internal documents."""
    return "\n".join(d.page_content for d in retriever.invoke(query))

tools = [search_docs]
llm_with_tools = llm.bind_tools(tools)

def agent(state: S) -> S:
    return {"messages": state["messages"] + [llm_with_tools.invoke(state["messages"])]}

g = StateGraph(S)
g.add_node("agent", agent)
g.add_node("tools", ToolNode(tools))
g.set_entry_point("agent")
g.add_conditional_edges("agent", tools_condition)
g.add_edge("tools", "agent")
app = g.compile()
```

---

# 🟨 PHASE 3 — Google Workspace Connectors (OAuth)

## Step 3.1 — OAuth 2.0 for Gmail (Read-Only)

**Status:** `[ ] pending`

### 📘 Notes
- **OAuth 2.0** lets a user grant your app limited access without sharing their password.
- **Scopes** define what you can do. Least privilege: only request what you need.
- For server-to-server (no user), use a **Service Account with domain-wide delegation**.

### ❓ Questions
1. Why is a *service account* different from a *user OAuth flow*?
2. What could go wrong if you request `gmail.modify` when you only need `gmail.readonly`?

### 💡 Hints
- Create a Google Cloud project, enable Gmail API, download `credentials.json`.
- Store tokens in `token.json`; never commit either file.
- Scope: `https://www.googleapis.com/auth/gmail.readonly`.

### 🧭 Approach
Write `auth.py` that performs the OAuth flow and saves a token. Write `gmail_tool.py` exposing `@tool def list_unread(n: int)` that returns the last `n` unread subjects. Verify with a manual script first, then wire it into the agent.

### 🆘 Answer (LAST RESORT)
```python
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os, pickle

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def get_service():
    creds = None
    if os.path.exists("token.pkl"):
        creds = pickle.load(open("token.pkl", "rb"))
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
        pickle.dump(creds, open("token.pkl", "wb"))
    return build("gmail", "v1", credentials=creds)

@tool
def list_unread(n: int = 5) -> str:
    """List unread Gmail subjects."""
    svc = get_service()
    res = svc.users().messages().list(userId="me", q="is:unread", maxResults=n).execute()
    return str([m["id"] for m in res.get("messages", [])])
```

---

## Step 3.2 — Calendar & Docs Tools

**Status:** `[ ] pending`

### 📘 Notes
- Repeat the OAuth pattern for Calendar and Docs APIs.
- **Calendar scope:** `.../auth/calendar.events`.
- **Docs scope:** `.../auth/documents.readonly`.
- Add each as a `@tool` so the agent can call them.

### ❓ Questions
1. If a user says "schedule a meeting with Alice," which tools must fire and in what order?
2. How do you prevent the agent from creating *duplicate* events?

### 💡 Hints
- Require an explicit confirmation step in the graph before write actions.
- Log every tool call to a file for audit.

### 🧭 Approach
Add `create_event(summary, start_iso, end_iso)` and `read_doc(doc_id)` tools. Add a **human-in-the-loop** node (`interrupt_before=["write_tools"]`) so the user confirms before any write.

### 🆘 Answer (LAST RESORT)
```python
@tool
def create_event(summary: str, start_iso: str, end_iso: str) -> str:
    """Create a Calendar event (requires user confirmation)."""
    svc = build("calendar", "v3", credentials=get_service()._http.credentials)
    ev = {"summary": summary,
          "start": {"dateTime": start_iso},
          "end":   {"dateTime": end_iso}}
    return svc.events().insert(calendarId="primary", body=ev).execute()["htmlLink"]
```
Add `interrupt_before=["tools"]` in `app.compile()` to force user approval.

---

# 🟪 PHASE 4 — Multimodal Inputs

## Step 4.1 — Voice In / Voice Out

**Status:** `[ ] pending`

### 📘 Notes
- Pipeline: **STT → LLM → TTS**.
- Google Cloud Speech-to-Text and Text-to-Speech handle this well; Whisper + Coqui are open-source alternatives.

### ❓ Questions
1. What latency budget is acceptable for a conversational voice agent?
2. How do you handle interruptions (user speaks while agent is talking)?

### 💡 Hints
- Start with **file-based** audio (upload a `.wav`), then move to streaming.
- Use `pydub` to normalize audio to 16kHz mono.

### 🧭 Approach
Write `voice.py`: record → save `.wav` → STT → pass text to your agent → TTS → play output. Keep it single-turn first.

### 🆘 Answer (LAST RESORT)
```python
from google.cloud import speech, texttospeech
# STT
client = speech.SpeechClient()
audio = speech.RecognitionAudio(content=open("in.wav","rb").read())
cfg = speech.RecognitionConfig(encoding="LINEAR16", sample_rate_hertz=16000, language_code="en-US")
text = client.recognize(config=cfg, audio=audio).results[0].alternatives[0].transcript
# LLM
reply = app.invoke({"messages": [text]})["messages"][-1]
# TTS
tts = texttospeech.TextToSpeechClient()
resp = tts.synthesize_speech(
    input=texttospeech.SynthesisInput(text=reply),
    voice=texttospeech.VoiceSelectionParams(language_code="en-US"),
    audio_config=texttospeech.AudioConfig(audio_encoding="MP3"))
open("out.mp3","wb").write(resp.audio_content)
```

---

## Step 4.2 — Image Understanding

**Status:** `[ ] pending`

### 📘 Notes
- Multimodal LLMs (Gemini, GPT-4o) accept images directly.
- Use cases: OCR invoices, read charts, describe screenshots.

### ❓ Questions
1. When would you use a dedicated OCR model vs. a multimodal LLM?
2. How do you cite the image region an answer came from?

### 💡 Hints
- Start with a chart image and ask: "What's the trend?"
- Compare `gemini-1.5-flash` vs. `gpt-4o-mini` for cost/quality.

### 🧭 Approach
Add a `describe_image(path)` tool that base64-encodes the image and passes it to Gemini. Wire it into the agent so uploads route to the MediaAgent.

### 🆘 Answer (LAST RESORT)
```python
import base64, google.generativeai as genai
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

@tool
def describe_image(path: str) -> str:
    """Describe or extract info from an image."""
    b64 = base64.b64encode(open(path, "rb").read()).decode()
    return model.generate_content([{"mime_type": "image/png", "data": b64},
                                   "Describe this image."]).text
```

---

## Step 4.3 — Video Summarization

**Status:** `[ ] pending`

### 📘 Notes
- Two strategies: (a) Gemini 1.5's native video input; (b) sample frames + Whisper transcript → LLM summary.
- (b) is cheaper and works with any LLM.

### ❓ Questions
1. How many frames per minute give you "good enough" summaries?
2. What's lost when you ignore audio vs. ignore video?

### 💡 Hints
- Use `ffmpeg` to sample 1 frame / 5 seconds.
- Transcribe audio separately with Whisper.

### 🧭 Approach
Write `video_summary.py`: extract frames → caption each → transcribe audio → feed both to LLM asking for a 1-paragraph summary + 5 bullet takeaways.

### 🆘 Answer (LAST RESORT)
```python
import subprocess, whisper
subprocess.run(["ffmpeg","-i","v.mp4","-vf","fps=1/5","frames/f_%03d.png"])
caps = [describe_image.invoke(p) for p in sorted(glob("frames/*.png"))][:20]
audio_text = whisper.load_model("base").transcribe("v.mp4")["text"]
summary = llm.invoke(f"Frames: {caps}\nTranscript: {audio_text}\nSummarize in 1 para + 5 bullets.").content
```

---

# 🟥 PHASE 5 — Serverless Cloud Deploy

## Step 5.1 — Containerize with FastAPI

**Status:** `[ ] pending`

### 📘 Notes
- **Cloud Run** runs containers serverlessly. It needs a web server listening on `$PORT`.
- **FastAPI** + `uvicorn` is the standard Python choice.

### ❓ Questions
1. Why must your container not hardcode a port?
2. What secrets must NOT be baked into the image?

### 💡 Hints
- Use `gunicorn -k uvicorn.workers.UvicornWorker` for production.
- Keep the image small: `python:3.11-slim`.

### 🧭 Approach
Write `main.py` exposing `POST /chat` that calls your LangGraph app. Add `Dockerfile` and `.dockerignore`. Test locally with `docker run -p 8080:8080`.

### 🆘 Answer (LAST RESORT)
```python
# main.py
from fastapi import FastAPI
from pydantic import BaseModel
app = FastAPI()

class Q(BaseModel): text: str

@app.post("/chat")
def chat(q: Q):
    return {"reply": app_graph.invoke({"messages":[q.text]})["messages"][-1]}
```
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}
```

---

## Step 5.2 — Deploy to Cloud Run

**Status:** `[ ] pending`

### 📘 Notes
- Workflow: `gcloud builds submit` → Artifact Registry → `gcloud run deploy`.
- Secrets go to **Secret Manager**, mounted as env vars.
- Serverless scales to zero — you pay only for requests.

### ❓ Questions
1. Why is min-instances > 0 sometimes worth the cost?
2. How do you roll back a bad deploy in Cloud Run?

### 💡 Hints
- Use `--allow-unauthenticated` only for a demo. Real enterprise = IAP.
- Store `GEMINI_API_KEY` in Secret Manager.

### 🧭 Approach
Enable APIs (Run, Artifact Registry, Secret Manager). Build & push the image. Deploy with `--set-secrets`. Test with `curl`. Add a Cloud Run revision rollback in your runbook.

### 🆘 Answer (LAST RESORT)
```bash
gcloud services enable run.googleapis.com artifactregistry.googleapis.com secretmanager.googleapis.com
gcloud artifacts repositories create atlas --repository-format=docker --location=us-central1
gcloud builds submit --tag us-central1-docker.pkg.dev/$PROJECT/atlas/api
echo -n "$GEMINI_API_KEY" | gcloud secrets create gemini-key --data-file=-
gcloud run deploy atlas-api \
  --image us-central1-docker.pkg.dev/$PROJECT/atlas/api \
  --region us-central1 --allow-unauthenticated \
  --set-secrets GEMINI_API_KEY=gemini-key:latest
```

---

# 🟫 PHASE 6 — Enterprise Governance

## Step 6.1 — VPC Service Controls + CMEK

**Status:** `[ ] pending`

### 📘 Notes
- **VPC-SC** creates a perimeter so data can't leave your project.
- **CMEK** = you own the encryption keys (Cloud KMS) instead of Google-managed.
- **Model Armor** filters prompt injection / unsafe content.

### ❓ Questions
1. What incident does VPC-SC specifically prevent?
2. Who can decrypt data if you lose your CMEK key?

### 💡 Hints
- Enable Cloud KMS, create a keyring + key in the same region as your data.
- Apply the key to Cloud Storage, BigQuery, and Vertex AI resources.

### 🧭 Approach
Create a KMS keyring, grant the Cloud Run service account `encrypter/decrypter`. Create a VPC-SC perimeter around your project. Enable Model Armor on the Gemini endpoint. Document each control in `GOVERNANCE.md`.

### 🆘 Answer (LAST RESORT)
```bash
gcloud kms keyrings create atlas-kr --location=us-central1
gcloud kms keys create atlas-key --keyring=atlas-kr --location=us-central1 --purpose=encryption
gcloud kms keys add-iam-policy-binding atlas-key \
  --keyring=atlas-kr --location=us-central1 \
  --member=serviceAccount:$RUN_SA --role=roles/cloudkms.cryptoKeyEncrypterDecrypter
# VPC-SC via console or Terraform (google_access_context_manager_service_perimeter)
```

---

## Step 6.2 — Audit Logging & RBAC

**Status:** `[ ] pending`

### 📘 Notes
- Cloud Audit Logs capture every API call. Export to BigQuery for analysis.
- **RBAC**: `viewer`, `agent-user`, `admin` roles with least privilege.

### ❓ Questions
1. What fields must an audit log contain to satisfy SOC 2?
2. How would you detect anomalous usage (e.g., 1000 queries/minute)?

### 💡 Hints
- Create a log sink: `gcloud logging sinks create atlas-sink bigquery.googleapis.com/projects/$PROJECT/datasets/audit`.
- Add a scheduled query to flag spikes.

### 🧭 Approach
Enable Data Access audit logs for Vertex AI and Cloud Run. Export to BigQuery. Build a small dashboard (Looker Studio) with #requests/user, error rate, avg latency. Define three IAM roles and assign to test users.

### 🆘 Answer (LAST RESORT)
```bash
gcloud logging sinks create atlas-audit-sink \
  bigquery.googleapis.com/projects/$PROJECT/datasets/atlas_audit \
  --log-filter='resource.type="aiplatform.googleapis.com/Endpoint"'
gcloud projects add-iam-policy-binding $PROJECT \
  --member=user:alice@example.com --role=roles/aiplatform.user
```

---

# 🟧 PHASE 7 — Evaluation & Demo

## Step 7.1 — End-to-End Eval Harness

**Status:** `[ ] pending`

### 📘 Notes
- RAG metrics (RAGAS) + **agent trajectory accuracy** (did it call the right tools?).
- Build a **golden set** of 50 tasks with expected tool calls.

### ❓ Questions
1. How do you score a *partially correct* trajectory?
2. What's the difference between offline and online evaluation?

### 💡 Hints
- Log every tool call as JSON. Compare to expected list with a simple diff.
- Use LLM-as-judge for open-ended answers.

### 🧭 Approach
Create `eval/tasks.json` with `{input, expected_tools, expected_answer}`. Write a runner that executes each task and reports: tool-F1, answer-accuracy, latency, cost. Run on every PR via GitHub Actions.

### 🆘 Answer (LAST RESORT)
```python
import json, time
tasks = json.load(open("eval/tasks.json"))
for t in tasks:
    start = time.time()
    out = app.invoke({"messages": [t["input"]]})
    tools_called = [m.name for m in out["messages"] if hasattr(m, "name")]
    print(t["input"], "| tools:", tools_called, "| dt:", round(time.time()-start,2))
```

---

## Step 7.2 — Demo & Portfolio Write-Up

**Status:** `[ ] pending`

### 📘 Notes
- Recruiters read **README first**. Lead with architecture diagram + 3 killer features.
- Record a 2-minute Loom: ask a question → show tool calls → show audit log.

### ❓ Questions
1. What single sentence describes your project's value?
2. What's the most impressive technical detail you can show in 30 seconds?

### 💡 Hints
- Use Excalidraw for the diagram.
- Include a "What I'd do next" section — shows senior thinking.

### 🧭 Approach
Write `README.md`: problem → architecture diagram → demo GIF → tech stack → governance → eval scores → how to run → next steps. Pin the repo. Add it to LinkedIn with the one-liner from Phase 7 notes.

### 🆘 Answer (LAST RESORT)
> *"Atlas is a serverless multi-agent RAG platform on GCP that securely connects Gemini to Google Workspace via OAuth, supports text/voice/image/video input, and enforces enterprise governance through VPC-SC, CMEK, and full audit logging."*

Add this as your LinkedIn headline bullet and the first line of your resume project section.

---

## ✅ Progress Tracker

| Phase | Step | Status |
|-------|------|--------|
| 1 | 1.1 Env Setup | `[ ]` |
| 1 | 1.2 Naive RAG | `[ ]` |
| 1 | 1.3 RAGAS Eval | `[ ]` |
| 2 | 2.1 First Agent | `[ ]` |
| 2 | 2.2 Tool Calling | `[ ]` |
| 3 | 3.1 Gmail OAuth | `[ ]` |
| 3 | 3.2 Calendar/Docs | `[ ]` |
| 4 | 4.1 Voice | `[ ]` |
| 4 | 4.2 Image | `[ ]` |
| 4 | 4.3 Video | `[ ]` |
| 5 | 5.1 FastAPI + Docker | `[ ]` |
| 5 | 5.2 Cloud Run | `[ ]` |
| 6 | 6.1 VPC-SC + CMEK | `[ ]` |
| 6 | 6.2 Audit + RBAC | `[ ]` |
| 7 | 7.1 Eval Harness | `[ ]` |
| 7 | 7.2 Demo + README | `[ ]` |

---

## 🚦 Rules Reminder

> **You are the student. The AI is the tutor.**
> Climb the ladder one rung at a time. Only type `GIVE ME THE ANSWER` when you've genuinely exhausted 📘❓💡🧭 — and even then, write what you learned first.
