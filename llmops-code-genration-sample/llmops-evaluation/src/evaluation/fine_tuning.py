import json
from typing import Dict, Any, List
import os
from dotenv import load_dotenv
import time

from src.evaluation.evaluator import LLMEvaluator
from src.evaluation.metrics import CodeEvaluationMetrics

load_dotenv()

class FineTuningOptimizer:
    def __init__(self):
        self.evaluator = LLMEvaluator()
        self.results_path = os.getenv("RESULTS_OUTPUT_PATH")
        self.dataset_path = os.getenv("EVALUATION_DATASET_PATH")

    def load_baseline_results(self, model: str) -> List[Dict[str, Any]]:
        """ベースライン評価結果の読み込み"""
        results = []
        baseline_file = os.path.join(self.results_path, f"evaluation_{model}.jsonl")
        with open(baseline_file, 'r') as f:
            for line in f:
                results.append(json.loads(line))
        return results

    def analyze_baseline(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """ベースライン結果の分析"""
        analysis = {
            "avg_token_efficiency": sum(r["metrics"]["token_efficiency"] for r in results) / len(results),
            "avg_similarity": sum(r["metrics"]["similarity"] for r in results) / len(results),
            "avg_latency": sum(r["metrics"]["latency"] for r in results) / len(results),
            "total_tokens": sum(r["metrics"]["prompt_tokens"] + r["metrics"]["completion_tokens"] for r in results)
        }
        return analysis

    def generate_optimization_suggestions(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """最適化の提案生成"""
        suggestions = {
            "token_reduction": False,
            "quality_improvement": False,
            "latency_optimization": False,
            "proposed_changes": []
        }

        # トークン効率の改善提案
        if analysis["avg_token_efficiency"] < 0.8:
            suggestions["token_reduction"] = True
            suggestions["proposed_changes"].append({
                "target": "token_efficiency",
                "current": analysis["avg_token_efficiency"],
                "goal": 0.8,
                "suggestion": "プロンプトの簡潔化とコンテキスト最適化"
            })

        # 品質の改善提案
        if analysis["avg_similarity"] < 0.7:
            suggestions["quality_improvement"] = True
            suggestions["proposed_changes"].append({
                "target": "code_quality",
                "current": analysis["avg_similarity"],
                "goal": 0.7,
                "suggestion": "より具体的な制約とベストプラクティスの指定"
            })

        # レイテンシーの最適化提案
        if analysis["avg_latency"] > 2000:  # 2秒以上
            suggestions["latency_optimization"] = True
            suggestions["proposed_changes"].append({
                "target": "latency",
                "current": analysis["avg_latency"],
                "goal": 2000,
                "suggestion": "バッチ処理の最適化とキャッシュの活用"
            })

        return suggestions

    def apply_optimization(self, task: Dict[str, Any], suggestions: Dict[str, Any]) -> Dict[str, Any]:
        """最適化の適用"""
        optimized_task = task.copy()

        if suggestions["token_reduction"]:
            # プロンプトの最適化
            optimized_task["prompt"] = self._optimize_prompt(task["prompt"])

        if suggestions["quality_improvement"]:
            # 品質向上のための制約追加
            optimized_task["prompt"] = self._add_quality_constraints(task["prompt"])

        return optimized_task

    def _optimize_prompt(self, prompt: str) -> str:
        """プロンプトの最適化"""
        # プロンプトの簡潔化とフォーマット最適化
        lines = prompt.split("\n")
        optimized_lines = [line for line in lines if line.strip() and not line.startswith("#")]
        return "\n".join(optimized_lines)

    def _add_quality_constraints(self, prompt: str) -> str:
        """品質制約の追加"""
        quality_constraints = """
以下の品質基準を満たすコードを生成してください：
- 一貫した命名規則の使用
- 適切なエラーハンドリング
- コードの再利用性を考慮
- パフォーマンスを意識した実装
"""
        return prompt + "\n" + quality_constraints

    def run_optimization(self, model: str):
        """最適化プロセスの実行"""
        # ベースライン結果の分析
        baseline_results = self.load_baseline_results(model)
        analysis = self.analyze_baseline(baseline_results)
        suggestions = self.generate_optimization_suggestions(analysis)

        # 最適化の適用と評価
        optimized_results = []
        with self.evaluator.start_evaluation_run(f"optimized_{model}"):
            for task in baseline_results:
                optimized_task = self.apply_optimization(task, suggestions)
                
                # 最適化されたタスクの評価
                start_time = time.time()
                completion = "# Optimized code here"  # 実際のLLM呼び出しに置き換え
                end_time = time.time()
                
                metrics = CodeEvaluationMetrics.calculate_metrics(
                    optimized_task["prompt"],
                    completion,
                    task["reference"]
                )
                metrics["latency"] = (end_time - start_time) * 1000

                # 評価結果の記録
                self.evaluator.evaluate_generation(
                    prompt=optimized_task["prompt"],
                    model=model,
                    completion=completion,
                    metrics=metrics,
                    metadata={"optimization": suggestions}
                )

                optimized_results.append({
                    "task_id": task["task_id"],
                    "original_metrics": task["metrics"],
                    "optimized_metrics": metrics,
                    "optimization_applied": suggestions
                })

        # 最適化結果の保存
        output_file = os.path.join(self.results_path, f"optimization_{model}.jsonl")
        with open(output_file, 'w') as f:
            for result in optimized_results:
                f.write(json.dumps(result) + '\n')

        return optimized_results

if __name__ == "__main__":
    optimizer = FineTuningOptimizer()
    results = optimizer.run_optimization("test-model")
    print(f"Optimization completed. Results saved to {os.getenv('RESULTS_OUTPUT_PATH')}")