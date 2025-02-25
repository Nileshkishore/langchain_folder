# from langchain_ollama import OllamaLLM

# # Initialize the DeepSeek model using Ollama
# llm = OllamaLLM(model="deepseek-r1:8b")

# # Define a prompt
# prompt = "What is DeepSeek?"

# # Generate response
# response = llm.invoke(prompt)

# # Print the output
# print("Response:", response)


import mlflow
from langchain_ollama import OllamaLLM

@mlflow.trace
def run_llm(prompt):
    """
    Run the DeepSeek model via Ollama and track the execution with MLflow.
    
    Args:
        prompt (str): The input prompt for the LLM
        
    Returns:
        str: The model's response
    """
    # Initialize the DeepSeek model using Ollama
    llm = OllamaLLM(model="deepseek-r1:8b")
    
    # Generate response
    response = llm.invoke(prompt)
    
    # Log the input and output with MLflow
    mlflow.log_param("prompt", prompt)
    mlflow.log_metric("response_length", len(response))
    
    return response

# Set up MLflow tracking # Change this to your MLflow tracking server if needed
mlflow.set_experiment("deepseek-llm-experiment")

# Example usage
if __name__ == "__main__":
    # Sample prompt
    sample_prompt = "What is DeepSeek?"
    
    # Start an MLflow run
    with mlflow.start_run(run_name="deepseek_sample_run"):
        # Call the traced function
        result = run_llm(sample_prompt)
        
        # Print the output
        print("Prompt:", sample_prompt)
        print("\nResponse:", result)