import weaviate
import openai
import json
import os

# Initialize Weaviate client (v3 syntax)
client = weaviate.Client("http://localhost:9090")

# OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client (v1 format)
openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)

def retrieve_relevant_chunks(question):
    """Retrieve top passages from Weaviate based on semantic search"""
    response = (
        client.query
        .get("FlatlandText", ["title", "description", "raw_chunk"])
        .with_near_text({"concepts": [question]})
        .with_limit(5)
        .do()
    )

    results = response.get("data", {}).get("Get", {}).get("FlatlandText", [])
    return results

def generate_ai_response(question, passages):
    """Generate a GPT-4 response based on retrieved passages"""

    # Format passages into a readable context
    context = "\n\n".join([f"Title: {p['title']}\nExcerpt: {p['raw_chunk'][:500]}..." for p in passages])

    prompt = f"""You are an expert on the book *Flatland*.
Answer the question below using these excerpts:
    
{context}

Question: {question}
"""

    # **Fix**: Use OpenAI's new v1 API format
    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an AI assistant trained on *Flatland* and geometry."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    return response.choices[0].message.content

# MAIN FUNCTION
def ask_flatland_question():
    user_question = input("Ask a question about Flatland: ")

    print("\n🔍 Retrieving relevant passages...")
    passages = retrieve_relevant_chunks(user_question)

    if not passages:
        print("⚠️ No relevant passages found.")
        return

    print("\n✍️ Generating AI response...\n")
    answer = generate_ai_response(user_question, passages)

    print("=== AI Answer ===")
    print(answer)

if __name__ == "__main__":
    ask_flatland_question()