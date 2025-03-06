import json
import time
from typing import Dict, Any, List
import os
from dotenv import load_dotenv

from src.evaluation.evaluator import LLMEvaluator
from src.evaluation.metrics import CodeEvaluationMetrics

load_dotenv()

class EvaluationRunner:
    def __init__(self):
        self.evaluator = LLMEvaluator()
        self.dataset_path = os.getenv("EVALUATION_DATASET_PATH")
        self.results_path = os.getenv("RESULTS_OUTPUT_PATH")

    def load_tasks(self) -> List[Dict[str, Any]]:
        """評価タスクの読み込み"""
        tasks = []
        with open(self.dataset_path, 'r') as f:
            for line in f:
                tasks.append(json.loads(line))
        return tasks

    def run_evaluation(self, model: str):
        """評価の実行"""
        tasks = self.load_tasks()
        results = []

        with self.evaluator.start_evaluation_run(f"evaluation_{model}"):
            for task in tasks:
                # タスクの実行と評価
                start_time = time.time()
                
                # ここでLLMによるコード生成を実行（実際のLLM呼び出しコードに置き換え）
                completion = "# Generated code here"
                
                end_time = time.time()
                latency = (end_time - start_time) * 1000  # ミリ秒に変換

                # メトリクスの計算
                metrics = CodeEvaluationMetrics.calculate_metrics(
                    task['prompt'],
                    completion,
                    task['reference']
                )
                metrics['latency'] = latency

                # 評価結果の記録
                self.evaluator.evaluate_generation(
                    prompt=task['prompt'],
                    model=model,
                    completion=completion,
                    metrics=metrics,
                    metadata=task['metadata']
                )

                # 結果の保存
                result = {
                    'task_id': task['task_id'],
                    'model': model,
                    'metrics': metrics,
                    'metadata': task['metadata']
                }
                results.append(result)

        # 結果の保存
        os.makedirs(self.results_path, exist_ok=True)
        output_file = os.path.join(self.results_path, f"evaluation_{model}.jsonl")
        with open(output_file, 'w') as f:
            for result in results:
                f.write(json.dumps(result) + '\n')

        return results

if __name__ == "__main__":
    runner = EvaluationRunner()
    results = runner.run_evaluation("test-model")
    print(f"Evaluation completed. Results saved to {os.getenv('RESULTS_OUTPUT_PATH')}")