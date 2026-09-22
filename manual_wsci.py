from pathlib import Path
import ollama

question = """
I changed my university password this morning.
Now my Windows laptop won't connect to campus Wi-Fi,
but my phone still works.
"""

selected_files = [
    ## Grab only the files that actually matter for this Wi-Fi/password issue
    "knowledge/wifi_setup.txt",
    "knowledge/password_changes.txt"
]

context = ""

## Loop through our hand-picked files and dump their text into the context
for file_path in selected_files:
    path = Path(file_path)
    if path.exists():
        context += path.read_text(encoding='utf-8')
        context += "\n\n"

response = ollama.chat(model='qwen3:8b', messages=[
    {
        'role': 'system',
        'content': f"You are an IT support assistant. Answer the user's question using ONLY the following context:\n\n{context}"
    },
    {
        'role': 'user',
        'content': question
    }
])

print("Context characters:", len(context))
print("\n--- AI Response ---")
print(response['message']['content'])