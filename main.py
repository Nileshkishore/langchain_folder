import threading
from rag_system import RAGSystem

def main():
    # Initialize the RAG system
    rag_system = RAGSystem()

    while True:
        # Get user input
        user_input = input("\nAsk something (type 'exit' to quit): ")
        
        if user_input.lower() == "exit":
            print("Exiting chat...")
            break

        # Retrieve relevant documents
        top_doc, cosine_score, retrieved_docs = rag_system.retrieve_documents(user_input)
        
        # Get context from top document or use default message
        context = top_doc.page_content if top_doc else "No relevant document found."
        
        # Generate response
        result = rag_system.generate_response(user_input, context)
        
        # Display results
        rag_system.display_results(
            response=result.get("response", "No response generated."),
            context=context,
            cosine_score=cosine_score,
            retrieved_docs=retrieved_docs
        )
        print("🔢 **Cosine Similarity Score (Top Match):**", cosine_score)

        # Log to MLflow in background
        thread = threading.Thread(
            target=rag_system.mlflow_logger.log_rag_interaction,
            args=(user_input, f"Context: {context}\n\nQuestion: {user_input}", 
                  result, [top_doc] if top_doc else [], cosine_score)
        )
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    main()