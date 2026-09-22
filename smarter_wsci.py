from pathlib import Path
import ollama
import json

question = """
I changed my university password this morning.
Now my Windows laptop won't connect to campus Wi-Fi,
but my phone still works.
"""

## ---------------------------------------------------------
## 1. Save and load state (ISOLATE / WRITE phase)
## ---------------------------------------------------------
service_status = {
    "wifi": "operational"
}

state = {
    "problem": question,
    "wi_fi status": "operational",
    "wi-fi_check": True
}

# Dump the initial state to a JSON file
with open("state.json", "w", encoding='utf-8') as file:
    json.dump(state, file, indent=2)

# Read it back so we can feed it to the model later
with open("state.json", "r", encoding='utf-8') as file:
    current_state = json.load(file)

print("Current State Loaded:", current_state)


## ---------------------------------------------------------
## 2. Be smart about picking context files (SELECT)
## ---------------------------------------------------------
def select_context(user_question):
    q_lower = user_question.lower()
    files_to_read = []
    
    # Simple keyword matching - nothing too fancy
    if "wi-fi" in q_lower or "wifi" in q_lower:
        files_to_read.append("knowledge/wifi_setup.txt")
        files_to_read.append("knowledge/service_status.txt")
    if "password" in q_lower:
        files_to_read.append("knowledge/password_changes.txt")
    if "print" in q_lower:
        files_to_read.append("knowledge/printing.txt")
        
    # Throw them in a set to avoid duplicating any files
    return list(set(files_to_read))

selected_files = select_context(question)


## ---------------------------------------------------------
## 3. Read the chosen files and stitch them together
## ---------------------------------------------------------
context = ""
for file_path in selected_files:
    path = Path(file_path)
    if path.exists():
        context += path.read_text(encoding='utf-8')
        context += "\n"

# Tack on the current state we loaded earlier so the model knows what's up
context += f"\nCurrent IT System State:\n{json.dumps(current_state)}\n"


## ---------------------------------------------------------
## 4. Shrink the context down (COMPRESS)
## ---------------------------------------------------------
def compress_context(raw_context, user_question):
    # Ask Qwen to play detective and extract only the rules we actually need
    prompt = f"Please extract and summarize only the rules and instructions from the following text that are relevant to resolving this problem: '{user_question}'.\n\nText:\n{raw_context}"
    
    resp = ollama.chat(model='qwen3:8b', messages=[
        {'role': 'user', 'content': prompt}
    ])
    return resp['message']['content']

compressed_context = compress_context(context, question)
print("\nCompressed Context Length:", len(compressed_context))


## ---------------------------------------------------------
## 5. Get the final answer and force it into JSON format
## ---------------------------------------------------------
system_prompt = f"""
You are an IT support assistant. Answer the user's problem using ONLY this compressed context:
{compressed_context}

You MUST return your answer in strictly valid JSON format with exactly this structure:
{{
    "diagnosis": "Brief explanation of why it is not working",
    "solution": "Step-by-step instructions to fix the Windows laptop"
}}
"""

final_response = ollama.chat(model='qwen3:8b', messages=[
    {'role': 'system', 'content': system_prompt},
    {'role': 'user', 'content': question}
])

output_text = final_response['message']['content']
print("\n--- Final Response from Qwen ---")
print(output_text)

## ---------------------------------------------------------
## 6. Clean up the output and save the final state (WRITE)
## ---------------------------------------------------------
clean_text = output_text.strip()
if clean_text.startswith("```json"):
    clean_text = clean_text[7:]
elif clean_text.startswith("```"):
    clean_text = clean_text[3:]
if clean_text.endswith("```"):
    clean_text = clean_text[:-3]

try:
    final_state = json.loads(clean_text.strip())
    # Update the artifact with the model's diagnosis
    with open("final_state.json", "w", encoding='utf-8') as f:
        json.dump(final_state, f, indent=4)
    print("\nResult successfully structured and saved to final_state.json")
except Exception as e:
    print(f"\nFailed to save state. Model didn't return perfect JSON: {e}")