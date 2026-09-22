from pathlib import Path
import ollama

question = """
I changed my university password this morning.
Now my Windows laptop won't connect to campus Wi-Fi,
but my phone still works.
"""

context = ""

for file in Path("knowledge").glob("*.txt"):
    context += file.read_text(encoding='utf-8')
    context += "\n\n"

response = ollama.chat(model='qwen3:8b', messages=[
    {
        'role': 'system',
        'content': f"You are a university IT support assistant. Answer the user's question using ONLY the following context info:\n\n{context}"
    },
    {
        'role': 'user',
        'content': question
    }
])

print(
    "Context characters:",
    len(context)
)

print("\n--- AI Response ---")
print(response['message']['content'])