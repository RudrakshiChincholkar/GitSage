from groq import Groq
import os
from dotenv import load_dotenv
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL_NAME = "llama-3.1-8b-instant"

def generate_answer(context: str, question: str) -> str:
    prompt = f"""
You are GitSage, an expert assistant that answers questions about GitHub repositories.
Use ONLY the context provided. If the answer is not present, say "I don't know based on the repository."

Context:
{context}

Question:
{question}
"""

    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        max_tokens=512
    )

    return completion.choices[0].message.content.strip()
