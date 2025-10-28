import argparse, json, os, requests

SYSTEM_PROMPT = "You are a helpful on-device assistant. Be concise. For extraction tasks, output ONLY the requested JSON."

def load_all_tasks(task_root):
    tasks = []
    for cat in os.listdir(task_root):
        f = os.path.join(task_root, cat, "tasks.json")
        if os.path.isfile(f):
            items = json.load(open(f))
            for it in items:
                it["_category"] = cat
            tasks.extend(items)
    return tasks

def build_messages(item):
    cat = item.get("_category")
    if cat == "rag":
        content = f"Use the following context to answer the question.\n\nCONTEXT:\n{item.get('context','')}\n\nQUESTION:\n{item['input']}"
    else:
        content = item["input"]
    msgs = [
        {"role":"system","content": SYSTEM_PROMPT},
        {"role":"user","content": content}
    ]
    return msgs

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="http://localhost:11434", help="Ollama host base (no trailing slash)")
    ap.add_argument("--model", required=True, help="Model name as shown in `ollama list`")
    ap.add_argument("--task_root", default="taskpacks")
    ap.add_argument("--out", default="outputs/outputs.json")
    args = ap.parse_args()

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    tasks = load_all_tasks(args.task_root)
    out = {}

    for item in tasks:
        messages = build_messages(item)
        options = {}
        # Encourage JSON-only output for extraction tasks
        if item.get("_category") == "extraction":
            options["format"] = "json"

        payload = {
            "model": args.model,
            "messages": messages,
            "stream": False,
        }
        if options:
            payload["options"] = options

        try:
            resp = requests.post(f"{args.host}/api/chat", json=payload, timeout=120)
            resp.raise_for_status()
            data = resp.json()
            text = data.get("message", {}).get("content", "")
        except Exception as e:
            text = f"ERROR: {e}"
        out[item["id"]] = text

    with open(args.out, "w") as f:
        json.dump(out, f, indent=2)
    print(f"Wrote {args.out} with {len(out)} items.")

if __name__ == "__main__":
    main()
