import mlflow
import os
from dotenv import load_dotenv

load_dotenv()

class MLflowClient:
    def __init__(self):
        mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI"))
        self.experiment_name = "llm-evaluation"
        self.experiment = self._get_or_create_experiment()

    def _get_or_create_experiment(self):
        experiment = mlflow.get_experiment_by_name(self.experiment_name)
        if experiment is None:
            experiment_id = mlflow.create_experiment(self.experiment_name)
            experiment = mlflow.get_experiment(experiment_id)
        return experiment

    def start_run(self, run_name: str):
        return mlflow.start_run(experiment_id=self.experiment.experiment_id, 
                              run_name=run_name)

    def log_metrics(self, metrics: dict):
        mlflow.log_metrics(metrics)

    def log_params(self, params: dict):
        mlflow.log_params(params)

    def log_model_performance(self, model_name: str, metrics: dict, params: dict = None):
        with self.start_run(f"{model_name}_evaluation"):
            if params:
                self.log_params(params)
            self.log_metrics(metrics)

    def log_artifact(self, local_path: str):
        mlflow.log_artifact(local_path)