import argparse, json, os, time
import requests

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

def build_prompt(item):
    cat = item.get("_category")
    if cat == "rag":
        return f"Use the following context to answer the question.\n\nCONTEXT:\n{item.get('context','')}\n\nQUESTION:\n{item['input']}"
    else:
        return item["input"]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base_url", required=True, help="OpenAI-compatible base URL, e.g. http://localhost:8080/v1")
    ap.add_argument("--model", required=True, help="Model name for the endpoint")
    ap.add_argument("--task_root", default="taskpacks")
    ap.add_argument("--out", default="outputs/outputs.json")
    args = ap.parse_args()

    os.makedirs(os.path.dirname(args.out), exist_ok=True)

    tasks = load_all_tasks(args.task_root)
    session = requests.Session()
    out = {}

    for item in tasks:
        prompt = build_prompt(item)
        payload = {
            "model": args.model,
            "messages": [
                {"role":"system","content": SYSTEM_PROMPT},
                {"role":"user","content": prompt}
            ],
            "temperature": 0.0,
            "max_tokens": 256
        }
        try:
            resp = session.post(f"{args.base_url}/chat/completions", json=payload, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            text = data["choices"][0]["message"]["content"]
        except Exception as e:
            text = f"ERROR: {e}"
        out[item["id"]] = text

    with open(args.out, "w") as f:
        json.dump(out, f, indent=2)
    print(f"Wrote {args.out} with {len(out)} items.")

if __name__ == "__main__":
    main()
