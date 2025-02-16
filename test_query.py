import weaviate
import json

# Connect to Weaviate on port 8081
client = weaviate.Client("http://localhost:9090")

# Perform a vector search using OpenAI embeddings
query_result = (
    client.query
    .get("FlatlandText", ["title", "description"])
    .with_near_text({"concepts": ["higher dimensions beyond two"]})
    .with_limit(5)
    .do()
)

# Pretty-print results
print(json.dumps(query_result, indent=2))