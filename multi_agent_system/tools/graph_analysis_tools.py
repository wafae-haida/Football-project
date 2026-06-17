from pathlib import Path
import json
import csv
import uuid
import time
import shutil
from datetime import datetime
from typing import Type, Dict, Any, List

from pydantic import BaseModel, Field
from crewai.tools import BaseTool


class GraphAnalysisInput(BaseModel):
    data_file: str = Field(..., description="Fichier data produit par l'Agent 1")
    action_batches_dir: str = Field(..., description="Dossier des batches produits par l'Agent d'analyse des actions")
    spatial_batches_dir: str = Field(..., description="Dossier des batches produits par l'Agent d'analyse spatiale")


class GraphAnalysisTool(BaseTool):
    name: str = "outil_d_analyse_de_graphe"
    description: str = (
        "Extrait des caractéristiques relationnelles entre joueurs à partir "
        "des séquences d'actions enrichies spatialement."
    )
    args_schema: Type[BaseModel] = GraphAnalysisInput

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

    def _write_batch(
        self,
        rows: List[Dict[str, Any]],
        output_dir: Path,
        split_name: str,
        batch_number: int
    ) -> str:

        output_file = (
            output_dir /
            f"{split_name}_graph_analysis_batch_{batch_number:03d}.csv"
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
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _extract_graph_features(
        self,
        row: Dict[str, Any]
    ) -> Dict[str, Any]:

        players = []
        teams = []
        roles = []
        action_types = []
        edges = []

        pass_edges_count = 0
        pressure_count = 0
        offensive_actions_count = 0
        defensive_actions_count = 0

        offensive_types = {
            "Pass",
            "Ball Receipt*",
            "Carry",
            "Dribble",
            "Shot"
        }

        defensive_types = {
            "Duel",
            "Pressure",
            "Ball Recovery",
            "Interception",
            "Clearance",
            "Block",
            "Goal Keeper"
        }

        previous_player = None

        for i in range(1, 11):
            player = row.get(f"action_{i}_player")
            team = row.get(f"action_{i}_team")
            role = row.get(f"action_{i}_role")
            action_type = row.get(f"action_{i}_type")
            pass_recipient = row.get(f"action_{i}_pass_recipient")

            if player:
                players.append(player)

            if team:
                teams.append(team)

            if role:
                roles.append(role)

            if action_type:
                action_types.append(action_type)

            if action_type in offensive_types:
                offensive_actions_count += 1

            if action_type in defensive_types:
                defensive_actions_count += 1

            if action_type == "Pressure":
                pressure_count += 1

            if action_type == "Pass" and player and pass_recipient:
                edges.append((player, pass_recipient))
                pass_edges_count += 1

            if previous_player and player and previous_player != player:
                edges.append((previous_player, player))

            if player:
                previous_player = player

        unique_players = list(dict.fromkeys(players))
        unique_teams = list(dict.fromkeys(teams))
        unique_roles = list(dict.fromkeys(roles))
        unique_action_types = list(dict.fromkeys(action_types))
        unique_edges = list(dict.fromkeys(edges))

        player_action_counts = {}

        for player in players:
            player_action_counts[player] = player_action_counts.get(player, 0) + 1

        if player_action_counts:
            main_player = max(player_action_counts, key=player_action_counts.get)
            main_player_actions = player_action_counts[main_player]
        else:
            main_player = None
            main_player_actions = 0

        repeated_players_count = sum(
            1 for count in player_action_counts.values()
            if count > 1
        )

        team_transitions_count = 0

        for i in range(1, len(teams)):
            if teams[i] != teams[i - 1]:
                team_transitions_count += 1

        return {
            "sequence_num_players": len(unique_players),
            "sequence_num_teams": len(unique_teams),
            "sequence_num_roles": len(unique_roles),
            "sequence_num_action_types": len(unique_action_types),
            "sequence_num_edges": len(unique_edges),
            "sequence_pass_edges_count": pass_edges_count,
            "sequence_pressure_count": pressure_count,
            "sequence_offensive_actions_count": offensive_actions_count,
            "sequence_defensive_actions_count": defensive_actions_count,
            "sequence_repeated_players_count": repeated_players_count,
            "sequence_team_transitions_count": team_transitions_count,
            "sequence_has_team_transition": 1 if team_transitions_count > 0 else 0,
            "sequence_main_player": main_player,
            "sequence_main_player_actions": main_player_actions,
            "sequence_unique_players": " | ".join(unique_players),
            "sequence_unique_teams": " | ".join(unique_teams),
            "sequence_unique_roles": " | ".join(unique_roles),
            "sequence_edges": " | ".join(
                [f"{source} -> {target}" for source, target in unique_edges]
            )
        }

    def _run(
        self,
        data_file: str,
        action_batches_dir: str,
        spatial_batches_dir: str
    ) -> str:

        batch_size = 100000

        trace_id = str(uuid.uuid4())
        start_time = time.time()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        data_path = self._resolve_path(data_file)
        action_dir = self._resolve_path(action_batches_dir)
        spatial_dir = self._resolve_path(spatial_batches_dir)

        trace_dir = Path("multi_agent_system/traces_crewai_report")
        trace_dir.mkdir(parents=True, exist_ok=True)

        try:
            with open(data_path, "r", encoding="utf-8") as f:
                data_content = json.load(f)

            split_name = data_content.get(
                "split",
                data_path.stem.replace("_data", "")
            )

            output_dir = (
                Path("dataset/graph_analysis/data") /
                f"{split_name}_batches"
            )

            if output_dir.exists():
                shutil.rmtree(output_dir)

            output_dir.mkdir(parents=True, exist_ok=True)

            rows = []
            output_files = []
            batch_number = 1

            total_sequences = 0
            total_edges = 0
            total_sequences_with_edges = 0

            action_batch_files = sorted(action_dir.glob("*.csv"))
            spatial_batch_files = sorted(spatial_dir.glob("*.csv"))

            for batch_file in spatial_batch_files:
                with open(batch_file, "r", encoding="utf-8", newline="") as f:
                    reader = csv.DictReader(f)

                    for sequence_row in reader:
                        total_sequences += 1

                        row = dict(sequence_row)
                        graph_features = self._extract_graph_features(row)

                        row.update(graph_features)

                        total_edges += graph_features["sequence_num_edges"]

                        if graph_features["sequence_num_edges"] > 0:
                            total_sequences_with_edges += 1

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

            execution_time = round(time.time() - start_time, 2)

            trace_file = trace_dir / f"{split_name}_graph_analysis_trace.json"

            summary = {
                "split": split_name,
                "input_data_file": str(data_path),
                "input_action_batches_dir": str(action_dir),
                "input_spatial_batches_dir": str(spatial_dir),
                "output_graph_batches_dir": str(output_dir),
                "total_action_batch_files": len(action_batch_files),
                "total_spatial_batch_files": len(spatial_batch_files),
                "total_sequences": total_sequences,
                "total_edges": total_edges,
                "total_sequences_with_edges": total_sequences_with_edges,
                "batch_size": batch_size,
                "number_of_batches": len(output_files),
                "output_files": output_files,
                "execution_time_seconds": execution_time,
                "status": "SUCCESS"
            }

            trace_content = {
                "trace_id": trace_id,
                "timestamp": timestamp,
                "agent_or_service": "Agent d'analyse de graphe",
                "task": "Extraction des caractéristiques relationnelles entre joueurs",
                "inputs": [
                    str(data_path),
                    str(action_dir),
                    str(spatial_dir)
                ],
                "tools_or_functions_called": [
                    "outil_d_analyse_de_graphe"
                ],
                "outputs": output_files,
                "status": "SUCCESS",
                "error_message": None,
                "execution_time_seconds": execution_time
            }

            self._save_json(trace_content, trace_file)

            return json.dumps(summary, ensure_ascii=False, indent=2)

        except Exception as e:
            execution_time = round(time.time() - start_time, 2)
            split_name = data_path.stem.replace("_data", "")
            trace_file = trace_dir / f"{split_name}_graph_analysis_trace.json"

            trace_content = {
                "trace_id": trace_id,
                "timestamp": timestamp,
                "agent_or_service": "Agent d'analyse de graphe",
                "task": "Extraction des caractéristiques relationnelles entre joueurs",
                "inputs": [
                    str(data_path),
                    str(action_dir),
                    str(spatial_dir)
                ],
                "tools_or_functions_called": [
                    "outil_d_analyse_de_graphe"
                ],
                "outputs": [],
                "status": "FAILED",
                "error_message": str(e),
                "execution_time_seconds": execution_time
            }

            self._save_json(trace_content, trace_file)

            raise e