import os
from typing import Iterable, List, Mapping, MutableMapping, Sequence

from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL_NAME = "llama-3.3-70b-versatile"
MAX_CONTEXT_CHARS = 12000  # Simple safeguard for context window size


def _build_context_from_chunks(
    retrieved_chunks: Sequence[Mapping] | Sequence[MutableMapping],
    repo_summary: str = "",
) -> str:
    """
    Build a unified textual context from a sequence of chunk objects.
    """
    context_parts: List[str] = []

    # Add repo summary if available
    if repo_summary:
        context_parts.append("=== Repository Overview ===")
        context_parts.append(repo_summary)
        context_parts.append("")

    if not retrieved_chunks:
        return "\n".join(context_parts)

    context_parts.append("=== Relevant Code & Documentation ===")
    for i, chunk in enumerate(retrieved_chunks, 1):
        # Handle both dict and object-like formats
        if isinstance(chunk, dict):
            metadata = chunk.get("metadata", {}) or {}
            file_path = metadata.get("path") or metadata.get("file_path") or "Unknown file"
            content = chunk.get("document", "")
        else:
            metadata = getattr(chunk, "metadata", {}) or {}
            file_path = metadata.get("path") or metadata.get("file_path") or "Unknown file"
            content = getattr(chunk, "document", "")

        # Handle both string and list documents
        if isinstance(content, list):
            content = "\n".join(content)

        context_parts.append(f"\n--- Source {i}: {file_path} ---")
        context_parts.append(str(content))

    return "\n".join(context_parts)


def _truncate_context(context: str, max_chars: int = MAX_CONTEXT_CHARS) -> str:
    """
    Truncate context string to a safe maximum length to respect the model's
    context window, keeping the most recent parts (which are typically the
    most relevant chunks).
    """
    if len(context) <= max_chars:
        return context
    # Keep the tail of the context, which generally contains the most recent
    # retrieved chunks while avoiding blowing up the prompt size.
    return context[-max_chars:]


def generate_answer(context_or_chunks, question: str, repo_summary: str = "") -> str:
    """
    Generate an answer using Groq LLM.

    Handles two signatures:
    1. Old: generate_answer(context_string, question)
    2. New: generate_answer(chunks_list, question, repo_summary)
    """

    # Handle both old signature (string context) and new signature (list of chunks)
    if isinstance(context_or_chunks, str):
        # Old Q&A signature: context is a string
        context = context_or_chunks
    else:
        # New documentation signature: context is a list of chunk dicts
        retrieved_chunks: Iterable = context_or_chunks
        context = _build_context_from_chunks(retrieved_chunks, repo_summary=repo_summary)

    # Truncate context defensively to avoid exceeding model limits
    context = _truncate_context(context, MAX_CONTEXT_CHARS)

    # Create the prompt
    prompt = f"""You are GitSage, an expert assistant that answers questions about GitHub repositories.

Your task is to answer questions by analyzing the provided repository context, which may include:
- Code files and their contents
- File paths and directory structure
- Programming languages and frameworks (from imports, file extensions, and code patterns)
- Algorithms and data structures implemented
- Repository summaries and metadata

IMPORTANT INSTRUCTIONS:
1. You MAY infer information from code structure, filenames, directory organization, imports, and patterns
2. Use cautious, evidence-based language such as:
   - "This repository appears to..."
   - "Based on the code structure..."
   - "From the retrieved files, it can be inferred..."
   - "The code suggests..."
3. You MUST NOT hallucinate or claim libraries/frameworks/technologies that are not present in the context
4. If you see imports, file extensions, or code patterns, you can infer the tech stack
5. If you see algorithm implementations or data structures, you can infer the repository's purpose
6. If inference is not possible after reasoning through the context, you may say it's unclear - but only after attempting to reason from the available evidence
7. Ground all claims in the provided context - cite file paths, code snippets, or patterns when making inferences

Context:
{context}

Question:
{question}

Answer by analyzing the context and making reasonable inferences where appropriate. Use cautious language and cite evidence from the context.
"""

    # Diagnostic logging to help debugging when the chat returns empty
    try:
        print(f"[Groq] prompt length: {len(prompt)} chars")
    except Exception:
        pass

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=1024,
        )

        # Robustly extract text from possible response shapes
        text = None
        try:
            # preferred shape
            text = completion.choices[0].message.content
        except Exception:
            try:
                # fallback: some SDKs return .choices[0].text
                text = completion.choices[0].text
            except Exception:
                try:
                    # fallback: content may be nested differently
                    text = getattr(completion.choices[0], "message", {}).get("content")
                except Exception:
                    text = None

        if not text:
            print("[Groq] Warning: no text returned in completion object; returning explicit message.")
            return "I don't know based on the repository."

        return text.strip()
    except Exception as e:
        print("[Groq] Exception while calling Groq API:", repr(e))
        return f"Error generating answer: {e}"