from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()


client = Groq(api_key="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")
messages = [
    {"role": "system", "content": "You are an expert AI assistant. Give clear, structured, and helpful answers. If possible, explain with examples."}
]

while True:
    user_input = input("You: ")

    if user_input.lower() == "exit":
        break

    messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
       model="llama-3.1-8b-instant",   # free & fast model
        messages=messages
    )

    reply = response.choices[0].message.content

    messages.append({"role": "assistant", "content": reply})

    print("AI:", reply)