import json
import weaviate

# Initialize Weaviate client (with correct port 8081)
client = weaviate.Client("http://localhost:9090")

# Load data from flatland.json
with open("flatland.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Configure batch import for efficiency
client.batch.configure(batch_size=100)

# Start batch process
with client.batch as batch:
    print("📥 Starting data ingestion...")
    for i, item in enumerate(data):
        properties = {
            "title": item["title"],
            "description": item["description"],
            "key_terms": item["key_terms"],
            "chunk_number": item["chunk_number"],
            "raw_chunk": item["raw_chunk"],
        }

        batch.add_data_object(
            data_object=properties,
            class_name="FlatlandText"
        )

        if i % 50 == 0:
            print(f"✅ Processed {i}/{len(data)} records...")

print("🎉 Data ingestion completed successfully!")