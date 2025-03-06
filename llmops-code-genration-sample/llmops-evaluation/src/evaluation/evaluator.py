import time
from typing import Dict, Any
from src.integrations.langfuse_client import LangfuseClient
from src.integrations.mlflow_client import MLflowClient
from src.integrations.openllmetry_client import OpenLLMetryClient

class LLMEvaluator:
    def __init__(self):
        self.langfuse = LangfuseClient()
        self.mlflow = MLflowClient()
        self.openllmetry = OpenLLMetryClient()

    def evaluate_generation(self, 
                          prompt: str,
                          model: str,
                          completion: str,
                          metrics: Dict[str, float],
                          metadata: Dict[str, Any] = None):
        """
        LLM生成の評価を実行し、各ツールにメトリクスを記録
        """
        start_time = time.time()
        
        # OpenLLMetryでのトレース開始
        with self.openllmetry.create_span("llm_generation") as span:
            # Langfuseでの生成記録
            generation = self.langfuse.create_generation(
                name="code_generation",
                model=model,
                prompt=prompt,
                completion=completion,
                start_time=start_time,
                end_time=time.time(),
                tokens=len(prompt.split()) + len(completion.split())  # 簡易的なトークン数計算
            )

            # 各メトリクスの記録
            for metric_name, value in metrics.items():
                # Langfuseスコア
                self.langfuse.log_score(generation.id, metric_name, value)
                
                # MLflowメトリクス
                self.mlflow.log_metrics({metric_name: value})
                
                # OpenLLMetryメトリクス
                if metric_name == "latency":
                    self.openllmetry.record_latency(model, value)
                elif metric_name == "tokens":
                    self.openllmetry.record_tokens(model, int(value), "total")

            # メタデータの記録
            if metadata:
                self.mlflow.log_params(metadata)

            # OpenLLMetryリクエスト記録
            self.openllmetry.record_request(model, success=True)

    def start_evaluation_run(self, run_name: str):
        """新しい評価実行を開始"""
        return self.mlflow.start_run(run_name)

    def log_artifact(self, local_path: str):
        """評価結果のアーティファクトを保存"""
        self.mlflow.log_artifact(local_path)