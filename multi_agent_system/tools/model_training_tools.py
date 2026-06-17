from pathlib import Path
import json
import uuid
import time
import joblib
from datetime import datetime
from typing import Type, Dict, Any, List

import pandas as pd

from pydantic import BaseModel, Field
from crewai.tools import BaseTool

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    classification_report,
    confusion_matrix
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder


class ModelTrainingInput(BaseModel):
    train_action_batches_dir: str = Field(...)
    validation_action_batches_dir: str = Field(...)
    test_action_batches_dir: str = Field(...)

    train_spatial_batches_dir: str = Field(...)
    validation_spatial_batches_dir: str = Field(...)
    test_spatial_batches_dir: str = Field(...)

    train_graph_batches_dir: str = Field(...)
    validation_graph_batches_dir: str = Field(...)
    test_graph_batches_dir: str = Field(...)


class ModelTrainingTool(BaseTool):
    name: str = "outil_d_entrainement_du_modele"
    description: str = (
        "Entraîne un modèle de prédiction des événements clés à partir "
        "des sorties des agents d'action, spatial et graphe."
    )
    args_schema: Type[BaseModel] = ModelTrainingInput

    def _resolve_path(self, input_path: str) -> Path:
        path = Path(input_path)

        if path.exists():
            return path

        cleaned = input_path.replace("\\", "/")

        if "dataset/" in cleaned:
            cleaned = cleaned[cleaned.index("dataset/"):]
            path = Path(cleaned)

        if path.exists():
            return path

        raise FileNotFoundError(f"Chemin introuvable : {input_path}")

    def _load_batches(self, batches_dir: Path) -> pd.DataFrame:
        batch_files = sorted(batches_dir.glob("*.csv"))

        if not batch_files:
            raise FileNotFoundError(
                f"Aucun fichier CSV trouvé dans : {batches_dir}"
            )

        dataframes = []

        for file_path in batch_files:
            df = pd.read_csv(file_path, low_memory=False)
            dataframes.append(df)

        return pd.concat(dataframes, ignore_index=True)

    def _prepare_xy(self, df: pd.DataFrame):
        if "target_label" not in df.columns:
            raise ValueError("La colonne target_label est absente.")

        y = df["target_label"]

        excluded_columns = []

        for col in df.columns:
            if col == "target_label":
                continue

            if col.startswith("target_"):
                excluded_columns.append(col)

            elif col in [
                "match_id",
                "sequence_action_types",
                "sequence_players",
                "sequence_roles",
                "sequence_unique_players",
                "sequence_unique_teams",
                "sequence_unique_roles",
                "sequence_edges"
            ]:
                excluded_columns.append(col)

            elif "event_id" in col:
                excluded_columns.append(col)

            elif "timestamp" in col:
                excluded_columns.append(col)

            elif "player" in col:
                excluded_columns.append(col)

            elif "pass_recipient" in col:
                excluded_columns.append(col)

        X = df.drop(
            columns=excluded_columns + ["target_label"],
            errors="ignore"
        )

        return X, y

    def _build_pipeline(self, X: pd.DataFrame) -> Pipeline:
        numeric_features = X.select_dtypes(
            include=["int64", "float64", "int32", "float32", "bool"]
        ).columns.tolist()

        categorical_features = [
            col for col in X.columns
            if col not in numeric_features
        ]

        numeric_transformer = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="median"))
            ]
        )

        categorical_transformer = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="most_frequent")),
                (
                    "encoder",
                    OrdinalEncoder(
                        handle_unknown="use_encoded_value",
                        unknown_value=-1
                    )
                )
            ]
        )

        preprocessor = ColumnTransformer(
            transformers=[
                ("num", numeric_transformer, numeric_features),
                ("cat", categorical_transformer, categorical_features)
            ]
        )

        model = RandomForestClassifier(
            n_estimators=80,
            random_state=42,
            class_weight="balanced_subsample",
            n_jobs=-1,
            min_samples_leaf=2
        )

        return Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                ("model", model)
            ]
        )

    def _evaluate(
        self,
        model,
        X,
        y,
        split_name: str,
        metrics_dir: Path
    ) -> Dict[str, Any]:

        predictions = model.predict(X)

        accuracy = accuracy_score(y, predictions)

        precision, recall, f1, _ = precision_recall_fscore_support(
            y,
            predictions,
            average="weighted",
            zero_division=0
        )

        report = classification_report(
            y,
            predictions,
            zero_division=0,
            output_dict=True
        )

        labels = sorted(y.unique().tolist())

        cm = confusion_matrix(
            y,
            predictions,
            labels=labels
        )

        cm_df = pd.DataFrame(
            cm,
            index=labels,
            columns=labels
        )

        cm_file = metrics_dir / f"{split_name}_confusion_matrix.csv"
        report_file = metrics_dir / f"{split_name}_classification_report.json"

        cm_df.to_csv(cm_file, encoding="utf-8")

        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        return {
            "split": split_name,
            "accuracy": accuracy,
            "precision_weighted": precision,
            "recall_weighted": recall,
            "f1_weighted": f1,
            "confusion_matrix_file": str(cm_file),
            "classification_report_file": str(report_file)
        }

    def _save_json(self, data: Dict[str, Any], path: Path) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _run(
        self,
        train_action_batches_dir: str,
        validation_action_batches_dir: str,
        test_action_batches_dir: str,
        train_spatial_batches_dir: str,
        validation_spatial_batches_dir: str,
        test_spatial_batches_dir: str,
        train_graph_batches_dir: str,
        validation_graph_batches_dir: str,
        test_graph_batches_dir: str
    ) -> str:

        trace_id = str(uuid.uuid4())
        start_time = time.time()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        trace_dir = Path("multi_agent_system/traces_crewai_report")
        trace_dir.mkdir(parents=True, exist_ok=True)

        model_dir = Path("model")
        metrics_dir = model_dir / "metrics"

        model_dir.mkdir(parents=True, exist_ok=True)
        metrics_dir.mkdir(parents=True, exist_ok=True)

        model_file = model_dir / "event_prediction_model.pkl"
        metrics_summary_file = metrics_dir / "metrics_summary.json"

        try:
            train_action_dir = self._resolve_path(train_action_batches_dir)
            validation_action_dir = self._resolve_path(validation_action_batches_dir)
            test_action_dir = self._resolve_path(test_action_batches_dir)

            train_spatial_dir = self._resolve_path(train_spatial_batches_dir)
            validation_spatial_dir = self._resolve_path(validation_spatial_batches_dir)
            test_spatial_dir = self._resolve_path(test_spatial_batches_dir)

            train_graph_dir = self._resolve_path(train_graph_batches_dir)
            validation_graph_dir = self._resolve_path(validation_graph_batches_dir)
            test_graph_dir = self._resolve_path(test_graph_batches_dir)

            train_df = self._load_batches(train_graph_dir)
            validation_df = self._load_batches(validation_graph_dir)
            test_df = self._load_batches(test_graph_dir)

            X_train, y_train = self._prepare_xy(train_df)
            X_validation, y_validation = self._prepare_xy(validation_df)
            X_test, y_test = self._prepare_xy(test_df)

            pipeline = self._build_pipeline(X_train)

            pipeline.fit(X_train, y_train)

            joblib.dump(pipeline, model_file)

            validation_metrics = self._evaluate(
                pipeline,
                X_validation,
                y_validation,
                "validation",
                metrics_dir
            )

            test_metrics = self._evaluate(
                pipeline,
                X_test,
                y_test,
                "test",
                metrics_dir
            )

            execution_time = round(time.time() - start_time, 2)

            summary = {
                "status": "SUCCESS",
                "model_file": str(model_file),
                "metrics_dir": str(metrics_dir),
                "metrics_summary_file": str(metrics_summary_file),

                "inputs": {
                    "train_action_batches_dir": str(train_action_dir),
                    "validation_action_batches_dir": str(validation_action_dir),
                    "test_action_batches_dir": str(test_action_dir),

                    "train_spatial_batches_dir": str(train_spatial_dir),
                    "validation_spatial_batches_dir": str(validation_spatial_dir),
                    "test_spatial_batches_dir": str(test_spatial_dir),

                    "train_graph_batches_dir": str(train_graph_dir),
                    "validation_graph_batches_dir": str(validation_graph_dir),
                    "test_graph_batches_dir": str(test_graph_dir)
                },

                "dataset_shapes": {
                    "train": train_df.shape,
                    "validation": validation_df.shape,
                    "test": test_df.shape
                },

                "target_distribution": {
                    "train": y_train.value_counts().to_dict(),
                    "validation": y_validation.value_counts().to_dict(),
                    "test": y_test.value_counts().to_dict()
                },

                "validation_metrics": validation_metrics,
                "test_metrics": test_metrics,
                "execution_time_seconds": execution_time
            }

            self._save_json(summary, metrics_summary_file)

            trace_file = trace_dir / "model_training_trace.json"

            trace_content = {
                "trace_id": trace_id,
                "timestamp": timestamp,
                "agent_or_service": "Agent d'entraînement du modèle",
                "task": "Entraînement du modèle de prédiction des événements clés",
                "inputs": summary["inputs"],
                "tools_or_functions_called": [
                    "outil_d_entrainement_du_modele"
                ],
                "outputs": [
                    str(model_file),
                    str(metrics_summary_file),
                    validation_metrics["confusion_matrix_file"],
                    validation_metrics["classification_report_file"],
                    test_metrics["confusion_matrix_file"],
                    test_metrics["classification_report_file"]
                ],
                "status": "SUCCESS",
                "error_message": None,
                "execution_time_seconds": execution_time
            }

            self._save_json(trace_content, trace_file)

            return json.dumps(summary, ensure_ascii=False, indent=2)

        except Exception as e:
            execution_time = round(time.time() - start_time, 2)

            trace_file = trace_dir / "model_training_trace.json"

            trace_content = {
                "trace_id": trace_id,
                "timestamp": timestamp,
                "agent_or_service": "Agent d'entraînement du modèle",
                "task": "Entraînement du modèle de prédiction des événements clés",
                "inputs": {
                    "train_action_batches_dir": train_action_batches_dir,
                    "validation_action_batches_dir": validation_action_batches_dir,
                    "test_action_batches_dir": test_action_batches_dir,
                    "train_spatial_batches_dir": train_spatial_batches_dir,
                    "validation_spatial_batches_dir": validation_spatial_batches_dir,
                    "test_spatial_batches_dir": test_spatial_batches_dir,
                    "train_graph_batches_dir": train_graph_batches_dir,
                    "validation_graph_batches_dir": validation_graph_batches_dir,
                    "test_graph_batches_dir": test_graph_batches_dir
                },
                "tools_or_functions_called": [
                    "outil_d_entrainement_du_modele"
                ],
                "outputs": [],
                "status": "FAILED",
                "error_message": str(e),
                "execution_time_seconds": execution_time
            }

            self._save_json(trace_content, trace_file)

            raise e