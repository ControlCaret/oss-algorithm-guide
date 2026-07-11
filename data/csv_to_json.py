import csv
import json
import ast
import os

def main():
    csv_path = "leetcode_problems.csv"
    json_path = "leetcode_problems.json"
    
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found in current directory.")
        return

    problems = []
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tags = []
            if row.get("topic_tags"):
                raw_tags = row["topic_tags"].strip()
                try:
                    if raw_tags.startswith("[") and raw_tags.endswith("]"):
                        tags = ast.literal_eval(raw_tags)
                        if not isinstance(tags, list):
                            tags = [tags]
                    else:
                        tags = [t.strip() for t in raw_tags.split(",") if t.strip()]
                except Exception:
                    tags = [tag.strip() for tag in raw_tags.replace("[", "").replace("]", "").replace("'", "").split(",") if tag.strip()]
            
            is_premium = row.get("is_premium", "False").strip().lower() in ("true", "1")
            
            problems.append({
                "id": int(row["id"]) if row.get("id") else 0,
                "title": row.get("title", ""),
                "description": row.get("problem_description", ""),
                "tags": tags,
                "difficulty": row.get("difficulty", "Easy"),
                "is_premium": is_premium,
                "url": row.get("problem_URL", "")
            })
            
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(problems, f, ensure_ascii=False, indent=2)
        
    print(f"Successfully converted {len(problems)} problems to {json_path}")

if __name__ == "__main__":
    main()
