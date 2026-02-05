from groq import Groq
import os
from dotenv import load_dotenv
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL_NAME = "llama-3.3-70b-versatile"  

def generate_answer(context_or_chunks, question, repo_summary=""):
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
        retrieved_chunks = context_or_chunks
        
        # Build context from chunks
        context_parts = []
        
        # Add repo summary if available
        if repo_summary:
            context_parts.append("=== Repository Overview ===")
            context_parts.append(repo_summary)
            context_parts.append("")
        
        # Add retrieved chunks
        if retrieved_chunks:
            context_parts.append("=== Relevant Code & Documentation ===")
            for i, chunk in enumerate(retrieved_chunks, 1):
                # Handle both dict and object formats
                if isinstance(chunk, dict):
                    file_path = chunk.get("metadata", {}).get("path", "Unknown file")
                    content = chunk.get("document", "")
                else:
                    file_path = getattr(chunk, 'metadata', {}).get("path", "Unknown file")
                    content = getattr(chunk, 'document', "")
                
                # Handle both string and list documents
                if isinstance(content, list):
                    content = "\n".join(content)
                
                context_parts.append(f"\n--- Source {i}: {file_path} ---")
                context_parts.append(content)
        
        context = "\n".join(context_parts)
    
    # Create the prompt
    prompt = f"""You are GitSage, an expert assistant that answers questions about GitHub repositories.
Use ONLY the context provided. If the answer is not present, say "I don't know based on the repository."

Context:
{context}

Question:
{question}
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
                {"role": "user", "content": prompt}
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
                    text = getattr(completion.choices[0], 'message', {}).get('content')
                except Exception:
                    text = None

        if not text:
            print("[Groq] Warning: no text returned in completion object; returning explicit message.")
            return "I don't know based on the repository."

        return text.strip()
    except Exception as e:
        print("[Groq] Exception while calling Groq API:", repr(e))
        return f"Error generating answer: {e}"