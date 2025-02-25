import os
import threading
import mlflow
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from custom_ollama import OllamaLLMWithMetadata  # Your custom model

# Disable parallelism warning
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Define paths
persist_directory = "./chroma_db"  # ChromaDB directory
mlflow.set_experiment("LLM_RAG_Logging")  # Set MLflow experiment

# Load embedding model
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Initialize ChromaDB with the embedding function
vector_store = Chroma(persist_directory=persist_directory, embedding_function=embedding_model)

# Modify the OllamaLLMWithMetadata to include MLflow tracing
class TracedOllamaLLMWithMetadata(OllamaLLMWithMetadata):
    @mlflow.trace
    def invoke(self, prompt):
        return super().invoke(prompt)

# Load Llama 3.2 model with tracing
llm = TracedOllamaLLMWithMetadata(model="llama3.2")

# Function to log MLflow asynchronously but with proper run ID
def log_to_mlflow(run_id, user_input, prompt, result, retrieved_docs, cosine_score):
    # Set the active run to the run_id from the parent thread
    with mlflow.start_run(run_id=run_id):
        mlflow.log_param("model_used", result.get("model", "Unknown Model"))
        mlflow.log_param("user_prompt", user_input)
        mlflow.log_param("full_prompt", prompt)  # Logging full prompt
        
        # Log document file name instead of full content
        retrieved_doc_name = retrieved_docs[0].metadata.get("source", "Unknown File") if retrieved_docs else "No document found"
        mlflow.log_param("retrieved_doc_name", retrieved_doc_name)

        mlflow.log_metric("cosine_similarity", cosine_score)
        mlflow.log_metric("processing_time_us", result.get("total_duration", 0))

        # Token-related metrics
        prompt_tokens = result.get("prompt_tokens", 0)
        generated_tokens = result.get("generated_tokens", 0)
        
        mlflow.log_metric("prompt_tokens", prompt_tokens)
        mlflow.log_metric("generated_tokens", generated_tokens)

        # Cost calculations
        input_cost = (prompt_tokens / 1_000) * 0.003  # $3 per MTok
        output_cost = (generated_tokens / 1_000) * 0.015  # $15 per MTok
        total_cost = input_cost + output_cost

        mlflow.log_metric("input_cost_usd", round(input_cost, 6))
        mlflow.log_metric("output_cost_usd", round(output_cost, 6))
        mlflow.log_metric("total_cost_usd", round(total_cost, 6))

        # Log LLM response
        llm_response = result.get("response", "No response generated.")
        mlflow.log_text(llm_response, "llm_response.txt")
        mlflow.log_param("llm_response", llm_response)
        mlflow.log_metric("llm_response_length", len(llm_response))  # Log response length
        
        mlflow.set_tag("date_time", result.get("created_at", "Unknown Time"))

# Interactive RAG loop
@mlflow.trace
def process_query(user_input):
    # Retrieve most relevant documents
    retrieved_docs_with_scores = vector_store.similarity_search_with_score(user_input, k=4)  # Get top 4 matches

    # Pick the best document
    if retrieved_docs_with_scores:
        top_doc, cosine_score = retrieved_docs_with_scores[0]
        context = top_doc.page_content
    else:
        top_doc = None
        context = "No relevant document found."
        cosine_score = 0.0

    # Construct the full prompt
    prompt = f"Context: {context}\n\nQuestion: {user_input}"

    # Query Llama 3.2 with retrieved context
    result = llm.invoke(prompt)
    
    return result, context, cosine_score, retrieved_docs_with_scores, prompt, top_doc

# Keep track of background threads
background_threads = []

# Main loop
while True:
    # Ask user for input
    user_input = input("\nAsk something (type 'exit' to quit): ")
    
    if user_input.lower() == "exit":
        print("Exiting chat...")
        # Wait for any remaining background threads to complete
        for thread in background_threads:
            if thread.is_alive():
                thread.join(timeout=2.0)  # Wait for up to 2 seconds
        break

    # Start an MLflow run for this query
    with mlflow.start_run() as active_run:
        # Get the run ID for the background thread
        run_id = active_run.info.run_id
        
        # Process the query
        result, context, cosine_score, retrieved_docs_with_scores, prompt, top_doc = process_query(user_input)
        
        # Start background logging thread with the current run ID
        thread = threading.Thread(
            target=log_to_mlflow, 
            args=(run_id, user_input, prompt, result, [top_doc] if top_doc else [], cosine_score)
        )
        thread.daemon = True
        thread.start()
        
        # Track the thread
        background_threads.append(thread)
        
        # Clean up completed threads
        background_threads = [t for t in background_threads if t.is_alive()]
        
        # **1️⃣ Show model response first (better UX)**
        print("\n🤖 **Model Response:**", result.get("response", "No response generated."))
        print("\n📜 **Top Retrieved Document Snippet:**", context[:500])  # Show snippet
        print("🔢 **Cosine Similarity Score (Top Match):**", cosine_score)

        # **2️⃣ Show retrieved document info**
        if retrieved_docs_with_scores:
            print("\n📚 **Retrieved Documents and Scores:**")
            for i, (doc, score) in enumerate(retrieved_docs_with_scores, 1):
                doc_name = doc.metadata.get("source", "Unknown File")
                print(f"{i}. 🔹 **Doc:** {doc_name[:50]}... | 🔢 **Score:** {score:.4f}")
        else:
            print("⚠️ No relevant document found.")