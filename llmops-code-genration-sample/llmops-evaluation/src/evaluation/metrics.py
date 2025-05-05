from typing import Dict, Any
import difflib
import re

class CodeEvaluationMetrics:
    @staticmethod
    def calculate_similarity(reference: str, generated: str) -> float:
        """コード間の類似度を計算"""
        # 空白と改行を正規化
        ref_normalized = re.sub(r'\s+', ' ', reference).strip()
        gen_normalized = re.sub(r'\s+', ' ', generated).strip()
        
        # difflib.SequenceMatcherを使用して類似度を計算
        matcher = difflib.SequenceMatcher(None, ref_normalized, gen_normalized)
        return matcher.ratio()

    @staticmethod
    def calculate_token_efficiency(prompt: str, completion: str, reference: str) -> Dict[str, float]:
        """トークン効率性の計算"""
        prompt_tokens = len(prompt.split())
        completion_tokens = len(completion.split())
        reference_tokens = len(reference.split())
        
        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "reference_tokens": reference_tokens,
            "token_efficiency": reference_tokens / (prompt_tokens + completion_tokens)
        }

    @staticmethod
    def evaluate_code_quality(code: str) -> Dict[str, Any]:
        """コード品質の評価"""
        # 基本的なコード品質メトリクス
        metrics = {
            "line_count": len(code.splitlines()),
            "char_count": len(code),
            "avg_line_length": len(code) / max(len(code.splitlines()), 1),
            "empty_lines": len([l for l in code.splitlines() if not l.strip()]),
        }
        
        # コードの一貫性チェック
        indentation_patterns = re.findall(r'^\s+', code, re.MULTILINE)
        if indentation_patterns:
            metrics["consistent_indentation"] = len(set([len(p) for p in indentation_patterns])) == 1
        
        return metrics

    @staticmethod
    def calculate_metrics(prompt: str, completion: str, reference: str) -> Dict[str, Any]:
        """すべてのメトリクスを計算"""
        metrics = {}
        
        # 類似度
        metrics["similarity"] = CodeEvaluationMetrics.calculate_similarity(reference, completion)
        
        # トークン効率性
        metrics.update(CodeEvaluationMetrics.calculate_token_efficiency(prompt, completion, reference))
        
        # コード品質
        metrics.update(CodeEvaluationMetrics.evaluate_code_quality(completion))
        
        # 追加のメタメトリクス
        metrics["completion_ratio"] = len(completion) / len(reference)
        
        return metrics