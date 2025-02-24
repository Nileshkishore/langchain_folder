import threading
import streamlit as st
from rag_system import RAGSystem

def rag_interaction(system_prompt, user_input, assistant_prompt=None):
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
        
        if assistant_prompt:
            messages.append({"role": "assistant", "content": assistant_prompt})

        # Generate response
        result = rag_system.generate_response(messages, context)

        # Log to MLflow in the background
        thread = threading.Thread(
            target=rag_system.mlflow_logger.log_rag_interaction,
            args=(user_input, f"Context: {context}\n\nQuestion: {user_input}", system_prompt, 
                  result, [top_doc] if top_doc else [], cosine_score)
        )
        thread.daemon = True
        thread.start()

        return result.get("response", "No response generated.")

    except Exception as e:
        return f"Error: {str(e)}"

# Streamlit UI
def main():
    st.title("RAG Chatbot with Streamlit")

    system_prompt = st.text_area("System Prompt", "Provide system instructions")
    user_input = st.text_area("User Prompt", "Ask something")
    assistant_prompt = st.text_area("Assistant Prompt (Optional)", "")

    if st.button("Generate Response"):
        with st.spinner("Generating response..."):
            response = rag_interaction(system_prompt, user_input, assistant_prompt)
            st.write("### Answer:")
            st.success(response)

if __name__ == "__main__":
    main()
