import json
import os
from typing import List, Dict, Any
import glob

class DatasetGenerator:
    def __init__(self, cline_repo_path: str, output_path: str):
        self.cline_repo_path = cline_repo_path
        self.output_path = output_path

    def collect_code_samples(self) -> List[Dict[str, Any]]:
        """Clineリポジトリからコードサンプルを収集"""
        samples = []
        
        # ソースコードファイルを再帰的に検索
        for ext in ['.ts', '.js', '.py']:
            for filepath in glob.glob(f"{self.cline_repo_path}/**/*{ext}", recursive=True):
                with open(filepath, 'r') as f:
                    content = f.read()
                    
                    # 機能単位でサンプルを分割
                    if len(content.strip()) > 0:
                        samples.append({
                            'file_path': os.path.relpath(filepath, self.cline_repo_path),
                            'language': ext[1:],
                            'content': content,
                            'size': len(content),
                            'task_type': 'code_generation'
                        })
        
        return samples

    def generate_evaluation_tasks(self, samples: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """評価タスクの生成"""
        tasks = []
        
        for sample in samples:
            # コード生成タスクの作成
            task = {
                'task_id': f"task_{len(tasks)}",
                'type': 'code_generation',
                'prompt': f"以下の要件に基づいてコードを生成してください:\n" +
                         f"- 言語: {sample['language']}\n" +
                         f"- ファイル: {sample['file_path']}\n" +
                         f"- 機能要件: [機能の説明をここに記述]",
                'reference': sample['content'],
                'metadata': {
                    'language': sample['language'],
                    'file_path': sample['file_path'],
                    'original_size': sample['size']
                }
            }
            tasks.append(task)
        
        return tasks

    def save_dataset(self, tasks: List[Dict[str, Any]]):
        """評価データセットの保存"""
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        
        with open(self.output_path, 'w') as f:
            for task in tasks:
                f.write(json.dumps(task) + '\n')

    def generate(self):
        """データセット生成の実行"""
        samples = self.collect_code_samples()
        tasks = self.generate_evaluation_tasks(samples)
        self.save_dataset(tasks)
        return len(tasks)

if __name__ == "__main__":
    generator = DatasetGenerator(
        cline_repo_path=os.getenv("CLINE_REPO_PATH"),
        output_path=os.getenv("EVALUATION_DATASET_PATH")
    )
    num_tasks = generator.generate()
    print(f"Generated {num_tasks} evaluation tasks")