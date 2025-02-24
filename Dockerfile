# Use a lightweight base image with curl
FROM ubuntu:latest

# Set environment variables to avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install required dependencies
RUN apt update && apt install -y \
    curl wget git \
    && rm -rf /var/lib/apt/lists/*

# Download and install Ollama
RUN curl -fsSL https://ollama.com/install.sh | bash

# Expose the Ollama default API port
EXPOSE 11434

# Start Ollama in the background and download the Llama 3.2 model
RUN ollama serve & sleep 5 && ollama pull llama3.2

# Command to run Ollama when the container starts
CMD ["ollama", "serve"]
