"""
Module 3 — Flask RAG Web Application (app.py)
Course: Programming for AI

Loads prebuilt FAISS index + lecture chunks + summary from Modules 1 & 2,
then serves a chat interface where FLAN-T5 answers questions via RAG.
"""

import os
import numpy as np
import pandas as pd
import faiss
from flask import Flask, request, jsonify, render_template, redirect, url_for
from sentence_transformers import SentenceTransformer
from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch

# ──────────────────────────────────────────────
# App Initialization
# ──────────────────────────────────────────────
app = Flask(__name__)

# ──────────────────────────────────────────────
# 1. Load pre-built assets on startup
# ──────────────────────────────────────────────

# Paths — adjust if your files live elsewhere
SUMMARY_PATH      = "D:\\PAI TASKS\\Project(Task 13)\\summary.txt"
CHUNKS_CSV_PATH   = "D:\\PAI TASKS\\Project(Task 13)\\lecture_chunks.csv"
FAISS_INDEX_PATH  = "D:\\PAI TASKS\\Project(Task 13)\\lecture_index.index"

print("[INIT] Loading lecture assets...")

# Read the human-readable summary
with open(SUMMARY_PATH, "r", encoding="utf-8") as f:
    LECTURE_SUMMARY = f.read().strip()

# Load chunks DataFrame — must have a 'text' column (also accepts 'Chunk' for backwards compat)
chunks_df = pd.read_csv(CHUNKS_CSV_PATH)
# Normalize: if column is named 'Chunk', rename it to 'text'
if "Chunk" in chunks_df.columns:
    chunks_df.rename(columns={"Chunk": "text"}, inplace=True)
if "text" not in chunks_df.columns:
    raise ValueError("lecture_chunks.csv must contain a 'text' or 'Chunk' column. Found: " + str(list(chunks_df.columns)))

# Load FAISS index
faiss_index = faiss.read_index(FAISS_INDEX_PATH)
print(f"[INIT] FAISS index loaded — {faiss_index.ntotal} vectors.")

# ──────────────────────────────────────────────
# 2. Load Models
# ──────────────────────────────────────────────

print("[INIT] Loading SentenceTransformer (all-MiniLM-L6-v2)...")
embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

print("[INIT] Loading FLAN-T5 (google/flan-t5-base)...")
# Use 'google/flan-t5-small' for faster inference on low-memory machines
FLAN_MODEL_NAME = "google/flan-t5-base"
tokenizer = T5Tokenizer.from_pretrained(FLAN_MODEL_NAME)
flan_model = T5ForConditionalGeneration.from_pretrained(FLAN_MODEL_NAME)
flan_model.eval()  # inference mode — disables dropout

# Move to GPU if available for faster generation
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
flan_model.to(device)
print(f"[INIT] FLAN-T5 running on: {device}")

print("[INIT] All models loaded. Server ready.\n")


# ──────────────────────────────────────────────
# Helper — RAG pipeline
# ──────────────────────────────────────────────

def retrieve_top_chunks(question: str, top_k: int = 3) -> str:
    """
    Embeds the question, searches the FAISS index for the top_k
    most semantically similar chunks, and returns them joined as one context string.
    """
    # Embed the question into a 384-dim float32 vector
    query_vector = embedder.encode([question], convert_to_numpy=True).astype("float32")

    # FAISS search — returns distances and indices arrays of shape (1, top_k)
    distances, indices = faiss_index.search(query_vector, top_k)

    # Gather the matching chunk texts
    retrieved = []
    for idx in indices[0]:
        if 0 <= idx < len(chunks_df):
            retrieved.append(chunks_df.iloc[idx]["text"])

    # Join with separator so the LLM sees clear boundaries
    return "\n---\n".join(retrieved)


def generate_answer(question: str, context: str) -> str:
    """
    Builds the RAG prompt and runs FLAN-T5 to generate a natural answer.
    """
    prompt = (
        "Answer the question based only on the following context.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}\n\n"
        "Answer:"
    )

    # Tokenize — truncate long prompts to FLAN-T5's 512-token input limit
    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        max_length=512,
        truncation=True,
    ).to(device)

    # Generate with beam search for coherent, complete answers
    with torch.no_grad():
        output_ids = flan_model.generate(
            **inputs,
            max_new_tokens=200,       # maximum answer length
            num_beams=4,              # beam search width
            early_stopping=True,      # stop when all beams hit EOS
            no_repeat_ngram_size=3,   # avoid repetitive phrases
        )

    # Decode and strip special tokens
    answer = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    return answer.strip()


# ──────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────

@app.route("/")
def landing():
    """
    Render the landing page where the user submits a YouTube URL.
    """
    return render_template("landing.html")


@app.route("/chat")
def chat():
    """
    Render the chat UI.  The ?url= query-param is forwarded from the landing
    page and displayed in the navbar; the RAG pipeline always uses the
    pre-built FAISS index that was loaded at startup.
    """
    return render_template("index.html", summary=LECTURE_SUMMARY)


@app.route("/ask", methods=["POST"])
def ask():
    """
    POST /ask
    Body: { "question": "<user question>" }
    Returns: { "answer": "<FLAN-T5 generated answer>" }
    """
    data = request.get_json(force=True)
    question = data.get("question", "").strip()

    # Basic validation
    if not question:
        return jsonify({"error": "Question cannot be empty."}), 400

    # Step 1 — Retrieve relevant context via FAISS
    context = retrieve_top_chunks(question, top_k=3)

    # Step 2 — Generate answer with FLAN-T5
    answer = generate_answer(question, context)

    return jsonify({"answer": answer})


# ──────────────────────────────────────────────
# Entry Point
# ──────────────────────────────────────────────

if __name__ == "__main__":
    # debug=False for production; set to True during development
    app.run(host="0.0.0.0", port=5000, debug=False)