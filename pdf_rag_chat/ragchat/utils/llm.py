import os
from openai import OpenAI

def chat(messages, model=None, temperature=0.2):
    client = OpenAI()
    model = model or os.getenv("OPENAI_CHAT_MODEL", "gpt-4o")
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return resp.choices[0].message.content
