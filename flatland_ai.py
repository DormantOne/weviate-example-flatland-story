from flask import Flask, request, jsonify, render_template
import weaviate
import os

# Initialize Flask app
app = Flask(__name__)

# Initialize Weaviate client (v4 syntax)
client = weaviate.Client(
    url="http://localhost:9090",  # URL to your Weaviate instance
    additional_headers={
        "X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY")  # Your OpenAI API key
    }
)

@app.route("/")
def home():
    """Serve the HTML page."""
    return render_template("index.html")


@app.route("/query", methods=["POST"])
def process_query():
    """Process user queries and return AI-generated responses."""
    user_question = request.json.get("question")
    
    if not user_question:
        return jsonify({"error": "No question provided"}), 400

    try:
        # Generate search queries
        queries = generate_search_queries(user_question)

        # Retrieve relevant chunks from Weaviate
        chunk_numbers, chunk_details = get_relevant_chunks(queries)

        # Get full content for the retrieved chunks
        text_chunks = get_chunk_content(chunk_numbers)

        # Generate a response using OpenAI
        answer = synthesize_response(user_question, text_chunks)

        return jsonify({
            "question": user_question,
            "answer": answer,
            "sources": text_chunks
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def generate_search_queries(user_question):
    """Generate search queries using OpenAI."""
    prompt = f"""Given this question about Flatland: "{user_question}", generate 5 different search queries."""
    
    response = client.query.get("FlatlandText").with_near_text({"concepts": [user_question]}).do()
    
    return [
        f"Query {i+1}: {result.get('concept', '')}" 
        for i, result in enumerate(response.get("data", {}).get("Get", {}).get("FlatlandText", []))
    ]


def get_relevant_chunks(queries):
    """Retrieve relevant chunks from Weaviate."""
    chunks = set()
    chunk_details = []

    for query in queries:
        results = (
            client.query
            .get("FlatlandText")
            .with_properties(["chunk_number", "title", "description"])
            .with_near_text({"concepts": [query]})
            .with_limit(3)
            .do()
        )

        for result in results.get("data", {}).get("Get", {}).get("FlatlandText", []):
            chunks.add(result["chunk_number"])
            chunk_details.append({
                "chunk_number": result["chunk_number"],
                "query": query,
                "title": result["title"],
                "description": result["description"]
            })

    return list(chunks), chunk_details


def get_chunk_content(chunk_numbers):
    """Fetch full content for given chunk numbers."""
    text_content = []

    for chunk_num in chunk_numbers:
        result = (
            client.query
            .get("FlatlandText")
            .with_properties(["raw_chunk", "title", "description", "key_terms"])
            .with_where({"path": ["chunk_number"], "operator": "Equal", "valueInt": chunk_num})
            .do()
        )

        if result.get("data", {}).get("Get", {}).get("FlatlandText"):
            chunk = result["data"]["Get"]["FlatlandText"][0]
            text_content.append({
                "chunk_number": chunk_num,
                "title": chunk["title"],
                "description": chunk["description"],
                "content": chunk["raw_chunk"],
                "key_terms": chunk["key_terms"]
            })

    return text_content


def synthesize_response(user_question, text_chunks):
    """Generate final answer using OpenAI."""
    context = "\n\n".join([f"Passage {i+1} - {chunk['title']}:\n{chunk['content'][:500]}..." for i, chunk in enum
erate(text_chunks)])

    prompt = f"""Based on these excerpts from Flatland, answer: "{user_question}"
    
    Relevant excerpts:
    {context}
    
    Provide a detailed answer that:
    1. Directly addresses the question
    2. Uses specific examples from the text
    3. References which passage number you're drawing from
    4. Maintains the mathematical/geometric precision of the original text"""

    # Generate OpenAI response
    response = client.query.get("FlatlandText").with_additional().do()
    return "Answer Pending Fix"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, threaded=True)