import os
import yaml
import logging
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime
from functools import lru_cache

from langchain.schema import Document
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from custom_ollama import OllamaLLMWithMetadata
from mlflow_logger import MLflowLogger

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGSystem:
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the RAG system with configuration and components."""
        self.config = self._load_config(config_path)
        self._setup_environment()
        
        # Initialize components lazily
        self._vector_store = None
        self._llm = None
        self._embedding_model = None
        self.mlflow_logger = MLflowLogger(self.config)
        
        # Keep limited history
        self.session_history = []
        self.max_history = 3  # Reduced from 10 to 3 for better performance

    @property
    def vector_store(self):
        """Lazy initialization of vector store."""
        if self._vector_store is None:
            self._vector_store = self._initialize_vector_store()
        return self._vector_store

    @property
    def llm(self):
        """Lazy initialization of LLM."""
        if self._llm is None:
            self._llm = self._initialize_llm()
        return self._llm

    @property
    def embedding_model(self):
        """Lazy initialization of embedding model."""
        if self._embedding_model is None:
            self._embedding_model = HuggingFaceEmbeddings(
                model_name=self.config['model']['embedding_model']
            )
        return self._embedding_model

    @lru_cache(maxsize=1)
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file with caching."""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    def _setup_environment(self) -> None:
        """Set up environment variables."""
        os.environ["TOKENIZERS_PARALLELISM"] = self.config['environment']['tokenizers_parallelism']

    def _initialize_vector_store(self) -> Chroma:
        """Initialize vector store with optimized settings."""
        return Chroma(
            persist_directory=self.config['storage']['persist_directory'],
            embedding_function=self.embedding_model
        )

    def _initialize_llm(self) -> OllamaLLMWithMetadata:
        """Initialize LLM with optimized settings."""
        return OllamaLLMWithMetadata(
            model=self.config['model']['name'],
            temperature=0.1  # Lower temperature for faster responses
        )

    def retrieve_documents(self, query: str) -> Tuple[Optional[Document], float, List[Tuple[Document, float]]]:
        """Optimized document retrieval."""
        try:
            # Reduced k for faster retrieval
            k = min(self.config['retrieval'].get('top_k', 4), 2)
            
            retrieved_docs = self.vector_store.similarity_search_with_score(
                query,
                k=k,
            )
            
            if not retrieved_docs:
                return None, 0.0, []
                
            top_doc, cosine_score = retrieved_docs[0]
            return top_doc, cosine_score, retrieved_docs
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return None, 0.0, []
        
    def generate_response(self, user_input: str, context: str) -> dict:
        """Generate response with optimized prompt."""
        try:
            # Simplified prompt construction
            prompt = self._construct_minimal_prompt(user_input, context)
            
            # Generate response
            result = self.llm.invoke(prompt)
            
            # Update history (limited)
            if len(self.session_history) >= self.max_history:
                self.session_history.pop(0)
            self.session_history.append((user_input, result.get("response", "")))
            
            return result
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {"response": "Error generating response", "error": str(e)}

    def _construct_minimal_prompt(self, user_input: str, context: str) -> str:
        """Construct minimal prompt for faster processing."""
        return f"Context: {context[:1000]}\nQuestion: {user_input}"  # Limit context size

    def display_results(self, response: str, context: str, cosine_score: float, 
                       retrieved_docs: List[Tuple[Document, float]]) -> None:
        """Simplified results display."""
        print("\n🤖", response)
        
        if retrieved_docs:
            print("\n📚 Relevant docs:")
            for i, (doc, score) in enumerate(retrieved_docs, 1):
                doc_name = doc.metadata.get("source", "Unknown")
                print(f"{i}. {doc_name[:30]}... ({score:.2f})")

    def cleanup(self) -> None:
        """Minimal cleanup."""
        self.session_history.clear()