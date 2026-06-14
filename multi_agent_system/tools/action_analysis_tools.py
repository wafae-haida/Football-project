from pathlib import Path
import json
import csv
import uuid
import time
import shutil
from datetime import datetime
from typing import Type, Optional, Dict, Any, List

from pydantic import BaseModel, Field
from crewai.tools import BaseTool


class ActionAnalysisInput(BaseModel):
    data_file: str = Field(..., description="Chemin du fichier produit par l'Agent 1")


class ActionAnalysisTool(BaseTool):
    name: str = "outil_d_analyse_des_actions"
    description: str = (
        "Analyse les actions de jeu à partir des matchs validés, "
        "exclut les événements critiques cibles et génère des batches CSV."
    )
    args_schema: Type[BaseModel] = ActionAnalysisInput

    def _get_name(self, data: Dict[str, Any], *keys: str) -> Optional[str]:
        current = data
        for key in keys:
            if not isinstance(current, dict):
                return None
            current = current.get(key)
        if isinstance(current, dict):
            return current.get("name")
        return current

    def _is_target_event(self, event: Dict[str, Any]) -> bool:
        event_type = self._get_name(event, "type")

        if event_type in ["Foul Committed", "Foul Won", "Offside"]:
            return True

        if event_type == "Pass":
            pass_type = self._get_name(event, "pass", "type")
            pass_outcome = self._get_name(event, "pass", "outcome")

            if pass_type in ["Free Kick", "Corner"]:
                return True

            if pass_outcome == "Pass Offside":
                return True

        if event_type == "Shot":
            shot_type = self._get_name(event, "shot", "type")
            shot_outcome = self._get_name(event, "shot", "outcome")

            if shot_outcome == "Goal":
                return True

            if shot_type in ["Penalty", "Free Kick"]:
                return True

        return False

    def _extract_action_features(self, event: Dict[str, Any], match_id: str) -> Dict[str, Any]:
        event_type = self._get_name(event, "type")

        action_types = [
            "Pass", "Shot", "Carry", "Ball Receipt*", "Dribble",
            "Duel", "Pressure", "Ball Recovery", "Interception",
            "Clearance", "Block", "Miscontrol", "Dispossessed",
            "Dribbled Past", "Goal Keeper"
        ]

        row = {
            "match_id": match_id,
            "event_id": event.get("id"),
            "index": event.get("index"),
            "period": event.get("period"),
            "minute": event.get("minute"),
            "second": event.get("second"),
            "timestamp": event.get("timestamp"),
            "event_type": event_type,
            "team": self._get_name(event, "team"),
            "player": self._get_name(event, "player"),
            "position": self._get_name(event, "position"),
        }

        for action in action_types:
            column_name = (
                "is_"
                + action.lower()
                .replace(" ", "_")
                .replace("*", "")
                .replace("-", "_")
            )
            row[column_name] = 1 if event_type == action else 0

        row["is_offensive_action"] = 1 if event_type in [
            "Pass", "Shot", "Carry", "Dribble", "Ball Receipt*"
        ] else 0

        row["is_defensive_action"] = 1 if event_type in [
            "Duel", "Pressure", "Ball Recovery", "Interception",
            "Clearance", "Block", "Dribbled Past", "Goal Keeper"
        ] else 0

        row["is_other_action"] = 1 if event_type in [
            "Miscontrol", "Dispossessed"
        ] else 0

        row["pass_type"] = self._get_name(event, "pass", "type")
        row["pass_outcome"] = self._get_name(event, "pass", "outcome")
        row["shot_type"] = self._get_name(event, "shot", "type")
        row["shot_outcome"] = self._get_name(event, "shot", "outcome")
        row["dribble_outcome"] = self._get_name(event, "dribble", "outcome")
        row["duel_type"] = self._get_name(event, "duel", "type")
        row["duel_outcome"] = self._get_name(event, "duel", "outcome")

        return row

    def _write_batch(
        self,
        rows: List[Dict[str, Any]],
        output_dir: Path,
        split_name: str,
        batch_number: int
    ) -> str:
        output_file = output_dir / f"{split_name}_action_features_batch_{batch_number:03d}.csv"

        fieldnames = list(rows[0].keys())

        with open(output_file, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        return str(output_file)

    def _run(self, data_file: str) -> str:
        batch_size = 100000

        trace_id = str(uuid.uuid4())
        start_time = time.time()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        data_path = Path(data_file)

        trace_dir = Path("multi_agent_system/traces_crewai_report")
        trace_dir.mkdir(parents=True, exist_ok=True)

        try:
            if not data_path.exists():
                raise FileNotFoundError(f"Fichier data introuvable : {data_file}")

            with open(data_path, "r", encoding="utf-8") as f:
                data_content = json.load(f)

            valid_files = data_content.get("valid_files", [])
            split_name = data_content.get("split", data_path.stem.replace("_data", ""))

            output_dir = Path("dataset/action_analysis/data") / f"{split_name}_batches"
            report_dir = Path("dataset/action_analysis/rapports")

            if output_dir.exists():
                shutil.rmtree(output_dir)

            output_dir.mkdir(parents=True, exist_ok=True)
            report_dir.mkdir(parents=True, exist_ok=True)

            rows = []
            batch_number = 1
            output_files = []

            total_events = 0
            total_action_events = 0
            total_excluded_events = 0

            for file_path_str in valid_files:
                file_path = Path(file_path_str)
                match_id = file_path.stem

                with open(file_path, "r", encoding="utf-8") as f:
                    events = json.load(f)

                for event in events:
                    total_events += 1

                    if self._is_target_event(event):
                        total_excluded_events += 1
                        continue

                    rows.append(self._extract_action_features(event, match_id))
                    total_action_events += 1

                    if len(rows) >= batch_size:
                        output_files.append(
                            self._write_batch(rows, output_dir, split_name, batch_number)
                        )
                        rows = []
                        batch_number += 1

            if rows:
                output_files.append(
                    self._write_batch(rows, output_dir, split_name, batch_number)
                )

            report_file = report_dir / f"{split_name}_action_report.txt"

            report_text = (
                f"L'analyse des actions pour le split {split_name} a été réalisée avec succès. "
                f"Au total, {len(valid_files)} fichier(s) de match ont été parcourus. "
                f"L'agent a analysé {total_events} événement(s). "
                f"Après exclusion des événements critiques cibles, "
                f"{total_action_events} action(s) de jeu ont été conservées. "
                f"{total_excluded_events} événement(s) ont été exclus. "
                f"Les caractéristiques extraites ont été sauvegardées sous forme de batches CSV "
                f"dans le dossier {output_dir}. "
                f"La taille de batch utilisée est {batch_size}. "
                f"Nombre total de batches générés : {len(output_files)}."
            )

            with open(report_file, "w", encoding="utf-8") as f:
                f.write(report_text)

            execution_time = round(time.time() - start_time, 2)
            trace_file = trace_dir / f"{split_name}_action_analysis_trace.json"

            trace_content = {
                "trace_id": trace_id,
                "timestamp": timestamp,
                "agent_or_service": "Agent d'analyse des actions",
                "task": "Extraction des caractéristiques liées aux actions de jeu",
                "inputs": [str(data_path)],
                "tools_or_functions_called": ["outil_d_analyse_des_actions"],
                "outputs": output_files + [str(report_file)],
                "status": "SUCCESS",
                "error_message": None,
                "execution_time_seconds": execution_time
            }

            with open(trace_file, "w", encoding="utf-8") as f:
                json.dump(trace_content, f, ensure_ascii=False, indent=2)

            return (
                f"Action batches folder: {output_dir}\n"
                f"Report file: {report_file}\n"
                f"Trace file: {trace_file}\n"
                f"Status: SUCCESS\n"
                f"Batch size: {batch_size}\n"
                f"Number of batches: {len(output_files)}"
            )

        except Exception as e:
            execution_time = round(time.time() - start_time, 2)
            split_name = data_path.stem.replace("_data", "")
            trace_file = trace_dir / f"{split_name}_action_analysis_trace.json"

            trace_content = {
                "trace_id": trace_id,
                "timestamp": timestamp,
                "agent_or_service": "Agent d'analyse des actions",
                "task": "Extraction des caractéristiques liées aux actions de jeu",
                "inputs": [str(data_path)],
                "tools_or_functions_called": ["outil_d_analyse_des_actions"],
                "outputs": [],
                "status": "FAILED",
                "error_message": str(e),
                "execution_time_seconds": execution_time
            }

            with open(trace_file, "w", encoding="utf-8") as f:
                json.dump(trace_content, f, ensure_ascii=False, indent=2)

            raise e