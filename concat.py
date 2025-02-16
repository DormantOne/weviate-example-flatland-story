#!/usr/bin/env python3

import os

# List of files in the order you want them concatenated:
FILES_TO_CONCAT = [
    "app.py",
    "docker-compose.yml",
    "flatland_ai.py",
    "ingest_flatland.py",
    "rag_pipeline.py",
    "requirements.txt",
    "setup_schema.py",
    "start_server.py",
    "test_query.py"
]

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))

    for filename in FILES_TO_CONCAT:
        file_path = os.path.join(base_dir, filename)
        if os.path.isfile(file_path):
            print(f"\n{'='*60}")
            print(f"=== BEGIN FILE: {filename}")
            print(f"{'='*60}\n")
            with open(file_path, "r", encoding="utf-8") as f:
                print(f.read())
            print(f"\n{'='*60}")
            print(f"=== END FILE: {filename}")
            print(f"{'='*60}\n")
        else:
            print(f"WARNING: {filename} not found in {base_dir}.")

if __name__ == "__main__":
    main()
