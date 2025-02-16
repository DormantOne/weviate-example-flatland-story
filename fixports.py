#!/usr/bin/env python3
import os
import re

# List of files in which to update port references
FILES_TO_UPDATE = [
    "app.py",
    "flatland_ai.py",
    "ingest_flatland.py",
    "rag_pipeline.py",
    "test_query.py",
    "setup_schema.py",
    "docker-compose.yml"
]

def update_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        contents = f.read()

    original = contents

    # For most files, replace any Weaviate URL that uses 8080 or 8081 with 9090
    # Matches strings like "http://localhost:8080" or "http://localhost:8081"
    contents = re.sub(r"http://localhost:(8080|8081)", "http://localhost:9090", contents)

    # For docker-compose.yml, update port mapping if needed.
    # For example, change "8081:8080" to "9090:8080".
    if os.path.basename(filepath) == "docker-compose.yml":
        contents = re.sub(r'"8081:8080"', '"9090:8080"', contents)
        # In case the port mapping is not quoted, update that too.
        contents = re.sub(r"8081:8080", "9090:8080", contents)

    if contents != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(contents)
        print(f"[UPDATED] {filepath}")
    else:
        print(f"[NO CHANGE] {filepath}")

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    for filename in FILES_TO_UPDATE:
        filepath = os.path.join(base_dir, filename)
        if os.path.isfile(filepath):
            update_file(filepath)
        else:
            print(f"[WARNING] {filename} not found.")

if __name__ == "__main__":
    main()
