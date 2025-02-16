import weaviate

# For v3, you can pass the URL directly (adjust the port as needed)

client = weaviate.Client("http://localhost:8080", startup_period=260)
# Define the schema
schema = {
    "class": "FlatlandText",
    "description": "Segments from Flatland with descriptions and content",
    "vectorizer": "text2vec-openai",
    "moduleConfig": {
        "text2vec-openai": {
            "model": "text-embedding-3-small",  # Updated to new model
            "modelVersion": "latest"
        }
    },
    "properties": [
        {
            "name": "title",
            "dataType": ["text"],
            "description": "The title of the segment"
        },
        {
            "name": "description",
            "dataType": ["text"],
            "description": "Description of the segment",
            "moduleConfig": {
                "text2vec-openai": {
                    "skip": False,
                    "vectorizePropertyName": False
                }
            }
        },
        {
            "name": "key_terms",
            "dataType": ["text[]"],
            "description": "Key terms from the segment"
        },
        {
            "name": "chunk_number",
            "dataType": ["int"],
            "description": "The segment number"
        },
        {
            "name": "raw_chunk",
            "dataType": ["text"],
            "description": "The raw text content"
        }
    ]
}

# Attempt to delete any existing schema
try:
    client.schema.delete_class("FlatlandText")
    print("✅ Old schema deleted!")
except Exception as e:
    print(f"⚠️ Schema deletion skipped: {e}")

# Create the new schema
try:
    client.schema.create_class(schema)
    print("✅ Schema created successfully!")
except Exception as e:
    print(f"⚠️ Failed to create schema: {e}")
