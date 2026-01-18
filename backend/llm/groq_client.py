from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_answer(prompt: str):
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",  
        messages=[
            {"role": "system", "content": "You are a helpful code assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    return response.choices[0].message.content
