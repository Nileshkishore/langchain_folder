import threading
import gradio as gr
from rag_system import RAGSystem

def rag_interaction(user_input):
    # Initialize the RAG system
    rag_system = RAGSystem()

    # Retrieve relevant documents
    top_doc, cosine_score, retrieved_docs = rag_system.retrieve_documents(user_input)
    
    # Get context from top document or use default message
    context = top_doc.page_content if top_doc else "No relevant document found."
    
    # Generate response
    result = rag_system.generate_response(user_input, context)
    
    # Log to MLflow in background
    thread = threading.Thread(
        target=rag_system.mlflow_logger.log_rag_interaction,
        args=(user_input, f"Context: {context}\n\nQuestion: {user_input}", 
              result, [top_doc] if top_doc else [], cosine_score)
    )
    thread.daemon = True
    thread.start()

    # Return only the response to display in the output
    return result.get("response", "No response generated.")

def main():
    # Create the Gradio interface
    interface = gr.Interface(
        fn=rag_interaction,
        inputs=gr.Textbox(label="Ask something"),
        outputs=gr.Textbox(label="Answer")  # Only display the answer
    )
    
    # Launch the interface
    interface.launch()

if __name__ == "__main__":
    main()
