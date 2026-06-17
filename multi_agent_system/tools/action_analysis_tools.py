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
    data_file: str = Field(
        ...,
        description="Chemin du fichier produit par l'Agent 1"
    )


class ActionAnalysisTool(BaseTool):
    name: str = "outil_d_analyse_des_actions"
    description: str = (
        "Construit des séquences d'actions précédant les événements clés. "
        "Le tool produit les batches CSV et retourne un résumé JSON. "
        "Le rapport texte humain sera rédigé par l'agent CrewAI."
    )
    args_schema: Type[BaseModel] = ActionAnalysisInput

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

        raise FileNotFoundError(f"Fichier introuvable : {input_path}")

    def _get_name(self, data: Dict[str, Any], *keys: str) -> Optional[str]:
        current = data

        for key in keys:
            if not isinstance(current, dict):
                return None
            current = current.get(key)

        if isinstance(current, dict):
            return current.get("name")

        return current

    def _get_key_event_label(self, event: Dict[str, Any]) -> str:
        event_type = self._get_name(event, "type")

        if event_type == "Shot":
            if self._get_name(event, "shot", "outcome") == "Goal":
                return "But"
            if self._get_name(event, "shot", "type") == "Penalty":
                return "Penalty"

        if event_type in ["Foul Committed", "Foul Won"]:
            card = self._get_name(event, "foul_committed", "card")

            if card == "Yellow Card":
                return "Carton jaune"

            if card in ["Red Card", "Second Yellow"]:
                return "Carton rouge"

            return "Faute disciplinaire"

        if event_type == "Offside":
            return "Hors-jeu"

        if event_type == "Pass":
            pass_type = self._get_name(event, "pass", "type")
            pass_outcome = self._get_name(event, "pass", "outcome")

            if pass_type == "Corner":
                return "Corner"

            if pass_type == "Free Kick":
                return "Coup franc"

            if pass_outcome == "Pass Offside":
                return "Hors-jeu"

        return "Aucun"

    def _get_action_role(self, event: Dict[str, Any]) -> str:
        event_type = self._get_name(event, "type")

        roles = {
            "Pass": "Passeur",
            "Ball Receipt*": "Receveur",
            "Carry": "Porteur du ballon",
            "Dribble": "Dribbleur",
            "Shot": "Tireur",
            "Duel": "Joueur en duel",
            "Ball Recovery": "Récupérateur",
            "Interception": "Intercepteur",
            "Pressure": "Presseur",
            "Goal Keeper": "Gardien",
            "Clearance": "Dégageur",
            "Block": "Bloqueur",
            "Miscontrol": "Contrôle raté",
            "Dispossessed": "Joueur dépossédé",
            "Dribbled Past": "Joueur dépassé",
        }

        return roles.get(event_type, "Joueur impliqué")

    def _get_action_result(self, event: Dict[str, Any]) -> Optional[str]:
        event_type = self._get_name(event, "type")

        if event_type == "Pass":
            return self._get_name(event, "pass", "outcome") or "Complete"

        if event_type == "Shot":
            return self._get_name(event, "shot", "outcome")

        if event_type == "Dribble":
            return self._get_name(event, "dribble", "outcome")

        if event_type == "Duel":
            return (
                self._get_name(event, "duel", "outcome")
                or self._get_name(event, "duel", "type")
            )

        if event_type == "Ball Receipt*":
            return self._get_name(event, "ball_receipt", "outcome") or "Complete"

        return None

    def _is_usable_action(self, event: Dict[str, Any]) -> bool:
        event_type = self._get_name(event, "type")

        usable_actions = [
            "Pass",
            "Ball Receipt*",
            "Carry",
            "Dribble",
            "Shot",
            "Duel",
            "Pressure",
            "Ball Recovery",
            "Interception",
            "Clearance",
            "Block",
            "Miscontrol",
            "Dispossessed",
            "Dribbled Past",
            "Goal Keeper",
        ]

        return event_type in usable_actions

    def _build_row(
        self,
        match_id: str,
        target_event: Dict[str, Any],
        previous_actions: List[Dict[str, Any]],
        window_size: int,
    ) -> Dict[str, Any]:

        row = {
            "match_id": match_id,
            "target_event_id": target_event.get("id"),
            "target_index": target_event.get("index"),
            "target_period": target_event.get("period"),
            "target_minute": target_event.get("minute"),
            "target_second": target_event.get("second"),
            "target_timestamp": target_event.get("timestamp"),
            "target_label": self._get_key_event_label(target_event),
            "target_type": self._get_name(target_event, "type"),
            "target_team": self._get_name(target_event, "team"),
            "target_player": self._get_name(target_event, "player"),
            "target_position": self._get_name(target_event, "position"),
            "sequence_length": len(previous_actions),
        }

        for i in range(window_size):
            action_number = i + 1

            if i < len(previous_actions):
                action = previous_actions[i]

                row[f"action_{action_number}_event_id"] = action.get("id")
                row[f"action_{action_number}_index"] = action.get("index")
                row[f"action_{action_number}_timestamp"] = action.get("timestamp")
                row[f"action_{action_number}_minute"] = action.get("minute")
                row[f"action_{action_number}_second"] = action.get("second")
                row[f"action_{action_number}_type"] = self._get_name(action, "type")
                row[f"action_{action_number}_team"] = self._get_name(action, "team")
                row[f"action_{action_number}_player"] = self._get_name(action, "player")
                row[f"action_{action_number}_position"] = self._get_name(action, "position")
                row[f"action_{action_number}_role"] = self._get_action_role(action)
                row[f"action_{action_number}_result"] = self._get_action_result(action)
                row[f"action_{action_number}_pass_recipient"] = self._get_name(
                    action, "pass", "recipient"
                )
                row[f"action_{action_number}_under_pressure"] = action.get(
                    "under_pressure", False
                )
            else:
                row[f"action_{action_number}_event_id"] = None
                row[f"action_{action_number}_index"] = None
                row[f"action_{action_number}_timestamp"] = None
                row[f"action_{action_number}_minute"] = None
                row[f"action_{action_number}_second"] = None
                row[f"action_{action_number}_type"] = None
                row[f"action_{action_number}_team"] = None
                row[f"action_{action_number}_player"] = None
                row[f"action_{action_number}_position"] = None
                row[f"action_{action_number}_role"] = None
                row[f"action_{action_number}_result"] = None
                row[f"action_{action_number}_pass_recipient"] = None
                row[f"action_{action_number}_under_pressure"] = None

        row["sequence_action_types"] = " -> ".join(
            str(self._get_name(a, "type")) for a in previous_actions
        )

        row["sequence_players"] = " -> ".join(
            str(self._get_name(a, "player"))
            for a in previous_actions
            if self._get_name(a, "player") is not None
        )

        row["sequence_roles"] = " -> ".join(
            str(self._get_action_role(a)) for a in previous_actions
        )

        return row

    def _write_batch(
        self,
        rows: List[Dict[str, Any]],
        output_dir: Path,
        split_name: str,
        batch_number: int,
    ) -> str:

        output_file = (
            output_dir / f"{split_name}_action_analysis_batch_{batch_number:03d}.csv"
        )

        with open(output_file, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

        return str(output_file)

    def _save_json(self, data: Dict[str, Any], path: Path) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _run(self, data_file: str) -> str:
        window_size = 10
        batch_size = 100000

        trace_id = str(uuid.uuid4())
        start_time = time.time()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        data_path = self._resolve_path(data_file)

        trace_dir = Path("multi_agent_system/traces_crewai_report")
        trace_dir.mkdir(parents=True, exist_ok=True)

        try:
            with open(data_path, "r", encoding="utf-8") as f:
                data_content = json.load(f)

            valid_files = data_content.get("valid_files", [])
            split_name = data_content.get("split", data_path.stem.replace("_data", ""))

            output_dir = Path("dataset/action_analysis/data") / f"{split_name}_batches"

            if output_dir.exists():
                shutil.rmtree(output_dir)

            output_dir.mkdir(parents=True, exist_ok=True)

            rows = []
            output_files = []
            batch_number = 1

            total_events = 0
            total_usable_actions = 0
            total_key_events = 0
            total_sequences = 0
            total_without_context = 0
            label_counts = {}

            for file_path_str in valid_files:
                file_path = self._resolve_path(file_path_str)
                match_id = file_path.stem

                with open(file_path, "r", encoding="utf-8") as f:
                    events = json.load(f)

                action_buffer = []

                for event in events:
                    total_events += 1

                    label = self._get_key_event_label(event)

                    if label != "Aucun":
                        total_key_events += 1
                        label_counts[label] = label_counts.get(label, 0) + 1

                        previous_actions = action_buffer[-window_size:]

                        if not previous_actions:
                            total_without_context += 1
                            continue

                        row = self._build_row(
                            match_id=match_id,
                            target_event=event,
                            previous_actions=previous_actions,
                            window_size=window_size,
                        )

                        rows.append(row)
                        total_sequences += 1

                        if len(rows) >= batch_size:
                            output_files.append(
                                self._write_batch(
                                    rows=rows,
                                    output_dir=output_dir,
                                    split_name=split_name,
                                    batch_number=batch_number,
                                )
                            )
                            rows = []
                            batch_number += 1

                        continue

                    if self._is_usable_action(event):
                        action_buffer.append(event)
                        total_usable_actions += 1

            if rows:
                output_files.append(
                    self._write_batch(
                        rows=rows,
                        output_dir=output_dir,
                        split_name=split_name,
                        batch_number=batch_number,
                    )
                )

            execution_time = round(time.time() - start_time, 2)

            trace_file = trace_dir / f"{split_name}_action_analysis_trace.json"

            summary = {
                "split": split_name,
                "input_data_file": str(data_path),
                "output_batches_dir": str(output_dir),
                "total_match_files": len(valid_files),
                "total_events": total_events,
                "total_usable_actions": total_usable_actions,
                "total_key_events": total_key_events,
                "total_sequences": total_sequences,
                "total_without_context": total_without_context,
                "window_size": window_size,
                "batch_size": batch_size,
                "number_of_batches": len(output_files),
                "output_files": output_files,
                "label_counts": label_counts,
                "execution_time_seconds": execution_time,
                "status": "SUCCESS",
            }

            trace_content = {
                "trace_id": trace_id,
                "timestamp": timestamp,
                "agent_or_service": "Agent d'analyse des actions",
                "task": "Construction des séquences d'actions avant événements clés",
                "inputs": [str(data_path)],
                "tools_or_functions_called": ["outil_d_analyse_des_actions"],
                "outputs": output_files,
                "status": "SUCCESS",
                "error_message": None,
                "execution_time_seconds": execution_time,
            }

            self._save_json(trace_content, trace_file)

            return json.dumps(summary, ensure_ascii=False, indent=2)

        except Exception as e:
            execution_time = round(time.time() - start_time, 2)
            split_name = data_path.stem.replace("_data", "")
            trace_file = trace_dir / f"{split_name}_action_analysis_trace.json"

            trace_content = {
                "trace_id": trace_id,
                "timestamp": timestamp,
                "agent_or_service": "Agent d'analyse des actions",
                "task": "Construction des séquences d'actions avant événements clés",
                "inputs": [str(data_path)],
                "tools_or_functions_called": ["outil_d_analyse_des_actions"],
                "outputs": [],
                "status": "FAILED",
                "error_message": str(e),
                "execution_time_seconds": execution_time,
            }

            self._save_json(trace_content, trace_file)

            raise e