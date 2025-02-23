from langchain_ollama import OllamaLLM

# Initialize the DeepSeek model using Ollama
llm = OllamaLLM(model="deepseek-r1:8b")

# Define a prompt
prompt = "What is DeepSeek?"

# Generate response
response = llm.invoke(prompt)

# Print the output
print("Response:", response)
