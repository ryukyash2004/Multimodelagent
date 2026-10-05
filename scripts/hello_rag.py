"""
Simple local RAG demo.

Usage:
  python scripts/hello_rag.py --pdf data/report.pdf --question "What was revenue growth?"

If no PDF is provided or file not found, the script uses a short sample document.
This script prints the top retrieved chunks and the LLM answer.

Note: requires the packages from `requirements.txt` and Ollama running locally
("ollama" command). Adjust imports if your langchain packages differ.
"""
import argparse
import os
import json
import requests
import math
from typing import List

# Try modern LangChain import paths first, then fall back to older community packages.
try:
    # Preferred: modern langchain package structure
    from langchain.document_loaders import PyPDFLoader
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.vectorstores import Chroma
    # Ollama bindings may come from a separate provider package
    from langchain_ollama import OllamaEmbeddings, ChatOllama
    _IMPORT_OK = True
except Exception as e_modern:
    try:
        # Fallback to older community packages (may be deprecated)
        from langchain_community.document_loaders import PyPDFLoader
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        from langchain_community.vectorstores import Chroma
        from langchain_ollama import OllamaEmbeddings, ChatOllama
        _IMPORT_OK = True
        print("Note: using langchain_community compatibility imports (deprecated). Consider migrating to the latest LangChain packages.")
    except Exception as e_fallback:
        _IMPORT_OK = False
        print("Warning: langchain imports failed:", e_modern)
        print(e_fallback)
        print("Install/upgrade required packages, for example:")
        print("  python -m pip install --upgrade langchain chromadb langchain-ollama")


SAMPLE_TEXT = """
Acme Corp reported revenue growth of 12% year-over-year in Q3, driven by strong demand
in product lines A and B. Operating margin improved by 1.5 percentage points.
"""


def load_documents(pdf_path: str):
    if pdf_path and os.path.exists(pdf_path):
        print(f"Loading PDF: {pdf_path}")
        try:
            loader = PyPDFLoader(pdf_path)
            docs = loader.load()
            return docs
        except Exception as e:
            print("Failed to load PDF with PyPDFLoader:", e)
    print("Using sample document text.")
    from langchain.schema import Document

    return [Document(page_content=SAMPLE_TEXT, metadata={"source": "sample"})]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", help="Path to PDF document", default="data/report.pdf")
    parser.add_argument("--question", help="Question to ask", default="What was revenue growth?")
    args = parser.parse_args()

    docs = load_documents(args.pdf)

    # Split into chunks
    try:
        splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
        chunks = splitter.split_documents(docs)
    except Exception:
        # fallback simple split
        chunks = []
        for d in docs:
            text = d.page_content
            for i in range(0, len(text), 800):
                chunks.append(type(d)(page_content=text[i:i+800], metadata=getattr(d, 'metadata', {})))

    print(f"Created {len(chunks)} chunks (showing up to 3):")
    for c in chunks[:3]:
        print("-", c.page_content.replace('\n', ' ')[:200])

    # Compute embeddings for chunks (try Ollama HTTP embed endpoint, fallback to sentence-transformers)
    def try_ollama_embed(text: str):
        # Try a few common Ollama endpoints/JSON shapes
        endpoints = [
            ("http://localhost:11434/api/embed?model=nomic-embed-text", {"input": text}),
            ("http://localhost:11434/embed?model=nomic-embed-text", {"input": text}),
            ("http://localhost:11434/api/embed?model=nomic-embed-text", {"text": text}),
            ("http://localhost:11434/api/embed", {"model": "nomic-embed-text", "input": text}),
        ]
        for url, payload in endpoints:
            try:
                resp = requests.post(url, json=payload, timeout=5)
                if not resp.ok:
                    continue
                body = resp.json()
                # Common shapes: {'embedding': [...]}, {'data': [[...]]}, {'embeddings':[...]} 
                if isinstance(body, dict):
                    if "embedding" in body and isinstance(body["embedding"], list):
                        return body["embedding"]
                    if "embeddings" in body and isinstance(body["embeddings"], list):
                        return body["embeddings"][0]
                    if "data" in body and isinstance(body["data"], list):
                        # data could be list of dicts with 'embedding'
                        first = body["data"][0]
                        if isinstance(first, dict) and "embedding" in first:
                            return first["embedding"]
                        if isinstance(first, list):
                            return first
                # If server returned a raw array
                if isinstance(body, list):
                    return body
            except Exception:
                continue
        return None

    def try_sentence_transformers(text: str):
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer("all-MiniLM-L6-v2")
            vec = model.encode(text)
            return vec.tolist()
        except Exception:
            return None

    def get_embedding(text: str):
        v = try_ollama_embed(text)
        if v is not None:
            return v
        v = try_sentence_transformers(text)
        if v is not None:
            return v
        raise RuntimeError("No embedding backend available. Run Ollama with nomic-embed-text or install sentence-transformers.")

    # Build embeddings for chunks
    chunk_texts = [c.page_content for c in chunks]
    print("Computing embeddings for", len(chunk_texts), "chunks (this may take a moment)...")
    chunk_embeddings: List[List[float]] = []
    for t in chunk_texts:
        try:
            emb = get_embedding(t)
            chunk_embeddings.append(emb)
        except Exception as e:
            print("Embedding failed:", e)
            print("Skipping retrieval — printing top chunk and exiting.")
            if chunks:
                print("Top chunk:\n", chunks[0].page_content)
            return

    def cosine(a: List[float], b: List[float]) -> float:
        # safe cosine similarity
        if a is None or b is None:
            return -1.0
        sa = math.sqrt(sum(x * x for x in a))
        sb = math.sqrt(sum(x * x for x in b))
        if sa == 0 or sb == 0:
            return -1.0
        return sum(x * y for x, y in zip(a, b)) / (sa * sb)

    # Retrieve context
    query = args.question
    try:
        q_emb = get_embedding(query)
    except Exception as e:
        print("Failed to embed query:", e)
        return

    sims = [cosine(q_emb, ce) for ce in chunk_embeddings]
    top_k = sorted(range(len(sims)), key=lambda i: sims[i], reverse=True)[:3]
    results = [chunks[i] for i in top_k]
    print("\nRetrieved context (k=3):")
    for r in results:
        print("- source:", getattr(r, 'metadata', {}).get('source', 'unknown'))
        print(r.page_content.strip()[:400])
        print('---')
    # LLM answer via local Ollama HTTP API (fallback to CLI call)
    context_text = "\n\n".join([r.page_content for r in results])
    prompt = f"Answer using only the context below.\n\nContext:\n\n{context_text}\n\nQuestion: {query}"

    # Try Ollama HTTP endpoint for generation
    def try_ollama_generate(prompt: str):
        url = "http://localhost:11434/api/generate?model=gemma3:4b"
        try:
            resp = requests.post(url, json={"prompt": prompt}, timeout=10)
            if resp.ok:
                body = resp.json()
                # look for a text field or 'content'
                if isinstance(body, dict):
                    # Common shapes: {'text': '...'} or {'choices':[{'text': '...'}]}
                    if "text" in body:
                        return body["text"]
                    if "content" in body:
                        return body["content"]
                    if "choices" in body and isinstance(body["choices"], list):
                        first = body["choices"][0]
                        if isinstance(first, dict) and "text" in first:
                            return first["text"]
                # fallback: return raw text
                return resp.text
        except Exception:
            return None

    ans = try_ollama_generate(prompt)
    if ans:
        print("\nAnswer:\n", ans)
        return

    # Fallback: call ollama CLI
    try:
        import subprocess
        p = subprocess.run(["ollama", "run", "gemma3:4b", prompt], capture_output=True, text=True, timeout=30)
        if p.returncode == 0:
            print("\nAnswer:\n", p.stdout.strip())
        else:
            print("LLM invocation failed (CLI):", p.stderr)
            print("Ensure Ollama is running and the model gemma3:4b is pulled.")
    except Exception as e:
        print("LLM invocation failed:", e)
        print("Ensure Ollama is running and the model gemma3:4b is pulled.")


if __name__ == "__main__":
    main()
