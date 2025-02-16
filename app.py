from flask import Flask, render_template, request, jsonify
import weaviate
from openai import OpenAI
import os

# Initialize Flask App
app = Flask(__name__)

# Weaviate Client (using port 8080)
client = weaviate.Client("http://localhost:8080")

# OpenAI Client initialization
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def generate_search_queries(user_question):
    """Generate potential search queries using LLM."""
    prompt = f"""Given this question about Flatland: "{user_question}"
    Generate 5 different search queries that could help find relevant information.
    Each query should be specific and focused on different aspects of the question.
    Format each query on a new line."""
    
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert at breaking down questions about Flatland into specific search queries."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip().split('\n')

def get_relevant_chunks(queries):
    """Get relevant chunk numbers from Weaviate based on queries."""
    chunks = set()
    chunk_details = []
    
    for query in queries:
        results = (client.query
            .get("FlatlandText", ["chunk_number", "title", "description"])
            .with_near_text({"concepts": [query]})
            .with_additional(["certainty"])
            .with_limit(3)
            .do())
        
        for result in results.get("data", {}).get("Get", {}).get("FlatlandText", []):
            chunks.add(result["chunk_number"])
            chunk_details.append({
                "chunk_number": result["chunk_number"],
                "query": query,
                "certainty": result.get("_additional", {}).get("certainty", 0),
                "title": result["title"],
                "description": result["description"]
            })
    
    return list(chunks), chunk_details

def get_chunk_content(chunk_numbers):
    """Fetch full content for given chunk numbers."""
    text_content = []
    
    for chunk_num in chunk_numbers:
        result = (client.query
            .get("FlatlandText", ["raw_chunk", "title", "description", "key_terms"])
            .with_where({
                "path": ["chunk_number"],
                "operator": "Equal",
                "valueInt": chunk_num
            })
            .do())
        
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
    """Generate final answer using LLM."""
    context = "\n\n".join([
        f"Passage {i+1} - {chunk['title']}:\n{chunk['content'][:500]}..."
        for i, chunk in enumerate(text_chunks)
    ])
    
    prompt = f"""Based on these excerpts from Flatland, answer: "{user_question}"
    
    Relevant excerpts:
    {context}
    
    Provide a detailed answer that:
    1. Directly addresses the question
    2. Uses specific examples from the text
    3. References which passage number you're drawing from
    4. Maintains the mathematical/geometric precision of the original text"""
    
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert on Flatland, providing precise and well-referenced answers."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/query", methods=["POST"])
def query():
    user_question = request.json.get("question", "").strip()

    if not user_question:
        return jsonify({"error": "No question provided"}), 400

    try:
        # Generate search queries
        queries = generate_search_queries(user_question)
        
        # Get relevant chunks
        chunk_numbers, chunk_details = get_relevant_chunks(queries)
        
        # Get full content
        text_chunks = get_chunk_content(chunk_numbers)
        
        # Generate final answer
        answer = synthesize_response(user_question, text_chunks)

        # Prepare search process details
        search_process = {
            "queries": queries,
            "chunk_details": chunk_details,
            "source_texts": text_chunks
        }

        # Return all data to frontend
        return jsonify({
            "question": user_question,
            "answer": answer,
            "search_process": search_process
        })

    except Exception as e:
        print(f"Error in /query endpoint: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
