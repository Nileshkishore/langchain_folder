import threading
import gradio as gr
from rag_system import RAGSystem

def rag_interaction(system_prompt, user_input, assistant_prompt=None):
    # Handle empty or None input
    if not user_input or not user_input.strip():
        return "Error: Please enter a valid question."

    try:
        # Initialize the RAG system
        rag_system = RAGSystem()

        # Retrieve relevant documents
        top_doc, cosine_score, retrieved_docs = rag_system.retrieve_documents(user_input)
        
        # Get context from top document or use default message
        context = top_doc.page_content if top_doc else "No relevant document found."
        
        # Construct full prompt for the model
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
        
        # If there's an assistant prompt (previous response), include it
        if assistant_prompt:
            messages.append({"role": "assistant", "content": assistant_prompt})

        # Generate response using structured messages
        result = rag_system.generate_response(messages, context)
        print(messages)
        
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

    except Exception as e:
        return f"Error: {str(e)}"

def main():
    # Create the Gradio interface with multiple inputs
    interface = gr.Interface(
        fn=rag_interaction,
        inputs=[
            gr.Textbox(label="System Prompt", placeholder="Provide system instructions"),
            gr.Textbox(label="User Prompt", placeholder="Ask something"),
            gr.Textbox(label="Assistant Prompt (Optional)", placeholder="Previous assistant response")  # Removed 'optional=True'
        ],
        outputs=gr.Textbox(label="Answer")  # Only display the answer
    )
    
    # Launch the interface
    interface.launch()


if __name__ == "__main__":
    main()
