from pathlib import Path
import json
import csv
import uuid
import time
import shutil
import math
from datetime import datetime
from typing import Type, Dict, Any, List

from pydantic import BaseModel, Field
from crewai.tools import BaseTool


PITCH_LENGTH = 120
PITCH_WIDTH = 80


class SpatialAnalysisInput(BaseModel):
    data_file: str = Field(
        ...,
        description="Fichier data produit par l'Agent 1"
    )

    action_batches_dir: str = Field(
        ...,
        description="Dossier des batches produits par l'Agent d'analyse des actions"
    )


class SpatialAnalysisTool(BaseTool):
    name: str = "outil_d_analyse_spatiale"
    description: str = (
        "Ajoute des caractéristiques spatiales aux séquences d'actions "
        "produites par l'Agent d'analyse des actions, sans charger tout le dataset en mémoire."
    )
    args_schema: Type[BaseModel] = SpatialAnalysisInput

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

    def _get_location(self, event: Dict[str, Any]):
        location = event.get("location")

        if isinstance(location, list) and len(location) >= 2:
            return location[0], location[1]

        return None, None

    def _distance_to_goal(self, x, y):
        if x is None or y is None:
            return None

        goal_x = PITCH_LENGTH
        goal_y = PITCH_WIDTH / 2

        return math.sqrt((goal_x - x) ** 2 + (goal_y - y) ** 2)

    def _field_zone(self, x):
        if x is None:
            return "Unknown"

        if x < 40:
            return "Zone défensive"

        if x < 80:
            return "Zone centrale"

        return "Zone offensive"

    def _build_match_file_map(
        self,
        valid_files: List[str]
    ) -> Dict[str, str]:

        match_file_map = {}

        for file_path_str in valid_files:
            file_path = self._resolve_path(file_path_str)
            match_id = file_path.stem
            match_file_map[match_id] = str(file_path)

        return match_file_map

    def _load_match_events_index(
        self,
        match_id: str,
        match_file_map: Dict[str, str]
    ) -> Dict[str, Dict[str, Any]]:

        if match_id not in match_file_map:
            return {}

        file_path = Path(match_file_map[match_id])

        with open(file_path, "r", encoding="utf-8") as f:
            events = json.load(f)

        event_index = {}

        for event in events:
            event_id = event.get("id")

            if event_id:
                event_index[event_id] = event

        return event_index

    def _write_batch(
        self,
        rows: List[Dict[str, Any]],
        output_dir: Path,
        split_name: str,
        batch_number: int
    ) -> str:

        output_file = (
            output_dir /
            f"{split_name}_spatial_analysis_batch_{batch_number:03d}.csv"
        )

        with open(output_file, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=list(rows[0].keys())
            )
            writer.writeheader()
            writer.writerows(rows)

        return str(output_file)

    def _save_json(
        self,
        data: Dict[str, Any],
        path: Path
    ) -> None:

        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=2
            )

    def _run(
        self,
        data_file: str,
        action_batches_dir: str
    ) -> str:

        batch_size = 100000

        trace_id = str(uuid.uuid4())
        start_time = time.time()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        data_path = self._resolve_path(data_file)
        action_dir = self._resolve_path(action_batches_dir)

        trace_dir = Path("multi_agent_system/traces_crewai_report")
        trace_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        try:
            with open(data_path, "r", encoding="utf-8") as f:
                data_content = json.load(f)

            split_name = data_content.get(
                "split",
                data_path.stem.replace("_data", "")
            )

            valid_files = data_content.get(
                "valid_files",
                []
            )

            output_dir = (
                Path("dataset/spatial_analysis/data") /
                f"{split_name}_batches"
            )

            if output_dir.exists():
                shutil.rmtree(output_dir)

            output_dir.mkdir(
                parents=True,
                exist_ok=True
            )

            match_file_map = self._build_match_file_map(
                valid_files
            )

            current_match_id = None
            current_event_index = {}

            rows = []
            output_files = []
            batch_number = 1

            total_sequences = 0
            total_actions_in_sequences = 0
            total_actions_with_location = 0
            total_actions_without_location = 0
            total_missing_match_files = 0

            action_batch_files = sorted(
                action_dir.glob("*.csv")
            )

            for batch_file in action_batch_files:

                with open(
                    batch_file,
                    "r",
                    encoding="utf-8",
                    newline=""
                ) as f:

                    reader = csv.DictReader(f)

                    for sequence_row in reader:

                        total_sequences += 1

                        match_id = sequence_row.get("match_id")

                        if match_id != current_match_id:

                            current_match_id = match_id

                            current_event_index = (
                                self._load_match_events_index(
                                    match_id,
                                    match_file_map
                                )
                            )

                            if not current_event_index:
                                total_missing_match_files += 1

                        x_values = []
                        y_values = []
                        distances = []
                        zones = []

                        row = dict(sequence_row)

                        for i in range(1, 11):

                            event_id = sequence_row.get(
                                f"action_{i}_event_id"
                            )

                            x = None
                            y = None
                            zone = "Unknown"
                            distance = None
                            has_location = 0

                            if event_id:

                                total_actions_in_sequences += 1

                                event = current_event_index.get(
                                    event_id
                                )

                                if event is not None:

                                    x, y = self._get_location(
                                        event
                                    )

                                    if x is not None and y is not None:

                                        zone = self._field_zone(x)

                                        distance = (
                                            self._distance_to_goal(
                                                x,
                                                y
                                            )
                                        )

                                        has_location = 1

                                        x_values.append(x)
                                        y_values.append(y)
                                        distances.append(distance)
                                        zones.append(zone)

                                        total_actions_with_location += 1

                                    else:
                                        total_actions_without_location += 1

                                else:
                                    total_actions_without_location += 1

                            row[f"action_{i}_x"] = x
                            row[f"action_{i}_y"] = y
                            row[f"action_{i}_zone"] = zone
                            row[f"action_{i}_distance_to_goal"] = distance
                            row[f"action_{i}_has_location"] = has_location

                        row["sequence_has_spatial_data"] = (
                            1 if x_values else 0
                        )

                        row["sequence_avg_x"] = (
                            sum(x_values) / len(x_values)
                            if x_values else None
                        )

                        row["sequence_avg_y"] = (
                            sum(y_values) / len(y_values)
                            if y_values else None
                        )

                        row["sequence_last_x"] = (
                            x_values[-1]
                            if x_values else None
                        )

                        row["sequence_last_y"] = (
                            y_values[-1]
                            if y_values else None
                        )

                        row["sequence_last_zone"] = (
                            zones[-1]
                            if zones else "Unknown"
                        )

                        row["sequence_min_distance_to_goal"] = (
                            min(distances)
                            if distances else None
                        )

                        row["sequence_avg_distance_to_goal"] = (
                            sum(distances) / len(distances)
                            if distances else None
                        )

                        row["sequence_count_defensive_zone"] = (
                            zones.count("Zone défensive")
                        )

                        row["sequence_count_middle_zone"] = (
                            zones.count("Zone centrale")
                        )

                        row["sequence_count_attacking_zone"] = (
                            zones.count("Zone offensive")
                        )

                        rows.append(row)

                        if len(rows) >= batch_size:
                            output_files.append(
                                self._write_batch(
                                    rows=rows,
                                    output_dir=output_dir,
                                    split_name=split_name,
                                    batch_number=batch_number
                                )
                            )

                            rows = []
                            batch_number += 1

            if rows:
                output_files.append(
                    self._write_batch(
                        rows=rows,
                        output_dir=output_dir,
                        split_name=split_name,
                        batch_number=batch_number
                    )
                )

            execution_time = round(
                time.time() - start_time,
                2
            )

            trace_file = (
                trace_dir /
                f"{split_name}_spatial_analysis_trace.json"
            )

            summary = {
                "split": split_name,
                "input_data_file": str(data_path),
                "input_action_batches_dir": str(action_dir),
                "output_spatial_batches_dir": str(output_dir),
                "total_match_files": len(valid_files),
                "total_action_batch_files": len(action_batch_files),
                "total_sequences": total_sequences,
                "total_actions_in_sequences": total_actions_in_sequences,
                "total_actions_with_location": total_actions_with_location,
                "total_actions_without_location": total_actions_without_location,
                "total_missing_match_files": total_missing_match_files,
                "batch_size": batch_size,
                "number_of_batches": len(output_files),
                "output_files": output_files,
                "execution_time_seconds": execution_time,
                "status": "SUCCESS"
            }

            trace_content = {
                "trace_id": trace_id,
                "timestamp": timestamp,
                "agent_or_service": "Agent d'analyse spatiale",
                "task": "Enrichissement spatial des séquences d'actions",
                "inputs": [
                    str(data_path),
                    str(action_dir)
                ],
                "tools_or_functions_called": [
                    "outil_d_analyse_spatiale"
                ],
                "outputs": output_files,
                "status": "SUCCESS",
                "error_message": None,
                "execution_time_seconds": execution_time
            }

            self._save_json(
                trace_content,
                trace_file
            )

            return json.dumps(
                summary,
                ensure_ascii=False,
                indent=2
            )

        except Exception as e:
            execution_time = round(
                time.time() - start_time,
                2
            )

            split_name = data_path.stem.replace(
                "_data",
                ""
            )

            trace_file = (
                trace_dir /
                f"{split_name}_spatial_analysis_trace.json"
            )

            trace_content = {
                "trace_id": trace_id,
                "timestamp": timestamp,
                "agent_or_service": "Agent d'analyse spatiale",
                "task": "Enrichissement spatial des séquences d'actions",
                "inputs": [
                    str(data_path),
                    str(action_dir)
                ],
                "tools_or_functions_called": [
                    "outil_d_analyse_spatiale"
                ],
                "outputs": [],
                "status": "FAILED",
                "error_message": str(e),
                "execution_time_seconds": execution_time
            }

            self._save_json(
                trace_content,
                trace_file
            )

            raise e