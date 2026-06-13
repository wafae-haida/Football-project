from pathlib import Path
import json
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import uuid
import time
from datetime import datetime


class DataProcessingInput(BaseModel):
    input_path: str = Field(
        ...,
        description="Chemin d'un dossier de split ou d'un fichier JSON StatsBomb"
    )


class DataProcessingTool(BaseTool):
    name: str = "outil_de_traitement_des_donnees"
    description: str = (
        "Traite un dossier de fichiers JSON StatsBomb ou un seul fichier JSON. "
        "Il vérifie les fichiers lisibles, compte les matchs et les événements, "
        "génère un fichier data JSON, un rapport texte et une trace d'exécution."
    )
    args_schema: Type[BaseModel] = DataProcessingInput

    def _run(self, input_path: str) -> str:
        trace_id = str(uuid.uuid4())
        start_time = time.time()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        path = Path(input_path)

        processing_dir = Path("dataset/processing")
        data_dir = processing_dir / "data"
        reports_dir = processing_dir / "rapports"
        trace_dir = Path("multi_agent_system/traces_crewai_report")

        data_dir.mkdir(parents=True, exist_ok=True)
        reports_dir.mkdir(parents=True, exist_ok=True)
        trace_dir.mkdir(parents=True, exist_ok=True)

        try:
            if not path.exists():
                raise FileNotFoundError(f"Chemin introuvable : {input_path}")

            if path.is_dir():
                json_files = list(path.glob("*.json"))
                split_name = path.name

            elif path.is_file() and path.suffix.lower() == ".json":
                json_files = [path]
                split_name = path.stem

            else:
                raise ValueError(
                    "Le chemin doit être un dossier contenant des fichiers JSON "
                    "ou un fichier JSON StatsBomb."
                )

            valid_files = []
            invalid_files = []
            total_events = 0

            for file_path in json_files:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        events = json.load(f)

                    if not isinstance(events, list):
                        invalid_files.append(str(file_path))
                        continue

                    valid_files.append(str(file_path))
                    total_events += len(events)

                except Exception:
                    invalid_files.append(str(file_path))

            status = "SUCCESS" if valid_files else "FAILED"
            data_status = "READY" if valid_files else "NOT_READY"

            data_file = data_dir / f"{split_name}_data.json"
            report_file = reports_dir / f"{split_name}_report.txt"
            trace_file = trace_dir / f"{split_name}_data_processing_trace.json"

            data_content = {
                "input_path": str(path),
                "split": split_name,
                "total_input_files": len(json_files),
                "total_valid_files": len(valid_files),
                "total_invalid_files": len(invalid_files),
                "total_events": total_events,
                "valid_files": valid_files,
                "invalid_files": invalid_files,
                "status": data_status,
            }

            with open(data_file, "w", encoding="utf-8") as f:
                json.dump(data_content, f, ensure_ascii=False, indent=2)

            if len(invalid_files) == 0:
                report_text = (
                    f"Le traitement de {input_path} a été réalisé avec succès. "
                    f"Au total, {len(json_files)} fichier(s) JSON ont été analysés. "
                    f"Tous les fichiers ont pu être lus correctement. "
                    f"L'ensemble contient {total_events} événements. "
                    f"Les données sont considérées comme exploitables pour les étapes suivantes du pipeline. "
                    f"La liste des fichiers exploitables a été enregistrée dans le fichier {data_file}."
                )
            else:
                report_text = (
                    f"Le traitement de {input_path} a été réalisé. "
                    f"Au total, {len(json_files)} fichier(s) JSON ont été analysés. "
                    f"{len(valid_files)} fichier(s) sont exploitables et {len(invalid_files)} fichier(s) sont invalides. "
                    f"Les fichiers exploitables contiennent {total_events} événements. "
                    f"La liste des fichiers exploitables et invalides a été enregistrée dans le fichier {data_file}."
                )

            with open(report_file, "w", encoding="utf-8") as f:
                f.write(report_text)

            execution_time = round(time.time() - start_time, 2)

            trace_content = {
                "trace_id": trace_id,
                "timestamp": timestamp,
                "agent_or_service": "Agent de traitement des données",
                "task": "Préparation du dataset",
                "inputs": [str(path)],
                "tools_or_functions_called": [
                    "outil_de_traitement_des_donnees"
                ],
                "outputs": [
                    str(data_file),
                    str(report_file)
                ],
                "status": status,
                "error_message": None,
                "execution_time_seconds": execution_time
            }

            with open(trace_file, "w", encoding="utf-8") as f:
                json.dump(trace_content, f, ensure_ascii=False, indent=2)

            return (
                f"Data file: {data_file}\n"
                f"Report file: {report_file}\n"
                f"Trace file: {trace_file}\n"
                f"Status: {data_status}"
            )

        except Exception as e:
            execution_time = round(time.time() - start_time, 2)
            split_name = path.stem if path.suffix.lower() == ".json" else path.name
            if not split_name:
                split_name = "unknown"

            trace_file = trace_dir / f"{split_name}_data_processing_trace.json"

            trace_content = {
                "trace_id": trace_id,
                "timestamp": timestamp,
                "agent_or_service": "Agent de traitement des données",
                "task": "Préparation du dataset",
                "inputs": [str(path)],
                "tools_or_functions_called": [
                    "outil_de_traitement_des_donnees"
                ],
                "outputs": [],
                "status": "FAILED",
                "error_message": str(e),
                "execution_time_seconds": execution_time
            }

            with open(trace_file, "w", encoding="utf-8") as f:
                json.dump(trace_content, f, ensure_ascii=False, indent=2)

            raise e