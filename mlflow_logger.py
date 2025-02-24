import mlflow
from typing import List, Dict, Any
from langchain.schema import Document

class MLflowLogger:
    def __init__(self, config: dict):
        self.config = config
        experiment_name = config['mlflow']['experiment_name']

        try:
            mlflow.set_experiment(experiment_name)
        except mlflow.exceptions.MlflowException:
            experiment_id = mlflow.create_experiment(experiment_name)
            mlflow.set_experiment(experiment_id)

    @mlflow.trace  # Logs function execution
    def log_rag_interaction(
        self,
        user_input: str,
        prompt: str,
        system_prompt: str,
        result: Dict[str, Any],
        retrieved_docs: List[Document],
        cosine_score: float
    ):
        with mlflow.start_run():
            self._log_basic_params(user_input, prompt, result, system_prompt)
            self._log_document_info(retrieved_docs)
            self._log_metrics(result, cosine_score)
            self._log_response_info(result)
            self._log_cost_metrics(result)
            self._log_tags(result)

    @mlflow.trace
    def _log_basic_params(self, user_input: str, prompt: str, result: Dict[str, Any], system_prompt: str):
        mlflow.log_param("model_used", result.get("model", "Unknown Model"))
        mlflow.log_param("user_prompt", user_input)
        mlflow.log_param("system_prompt", system_prompt)
        mlflow.log_param("full_prompt", prompt)

    @mlflow.trace
    def _log_document_info(self, retrieved_docs: List[Document]):
        retrieved_doc_name = (
            retrieved_docs[0].metadata.get("source", "Unknown File")
            if retrieved_docs and isinstance(retrieved_docs[0], Document)
            else "No document found"
        )
        mlflow.log_param("retrieved_doc_name", retrieved_doc_name)

    @mlflow.trace
    def _log_metrics(self, result: Dict[str, Any], cosine_score: float):
        mlflow.log_metric("cosine_similarity", cosine_score)
        mlflow.log_metric("processing_time_us", result.get("total_duration", 0))
        mlflow.log_metric("prompt_tokens", result.get("prompt_tokens", 0))
        mlflow.log_metric("generated_tokens", result.get("generated_tokens", 0))

    @mlflow.trace
    def _log_response_info(self, result: Dict[str, Any]):
        llm_response = result.get("response", "No response generated.")
        with open("llm_response.txt", "w") as f:
            f.write(llm_response)
        mlflow.log_artifact("llm_response.txt")
        mlflow.log_param("llm_response", llm_response)
        mlflow.log_metric("llm_response_length", len(llm_response))

    @mlflow.trace
    def _log_cost_metrics(self, result: Dict[str, Any]):
        prompt_tokens = result.get("prompt_tokens", 0)
        generated_tokens = result.get("generated_tokens", 0)

        input_cost = (prompt_tokens / 1_000) * self.config['costs']['input_cost_per_1k']
        output_cost = (generated_tokens / 1_000) * self.config['costs']['output_cost_per_1k']
        total_cost = input_cost + output_cost

        mlflow.log_metric("input_cost_usd", round(input_cost, 6))
        mlflow.log_metric("output_cost_usd", round(output_cost, 6))
        mlflow.log_metric("total_cost_usd", round(total_cost, 6))

    @mlflow.trace
    def _log_tags(self, result: Dict[str, Any]):
        mlflow.set_tag("date_time", result.get("created_at", "Unknown Time"))
