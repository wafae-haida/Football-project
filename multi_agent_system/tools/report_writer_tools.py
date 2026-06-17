from pathlib import Path
from typing import Type

from pydantic import BaseModel, Field
from crewai.tools import BaseTool


class ReportWriterInput(BaseModel):
    report_path: str = Field(..., description="Chemin du fichier rapport à créer")
    report_text: str = Field(..., description="Texte du rapport à sauvegarder")


class ReportWriterTool(BaseTool):
    name: str = "outil_de_redaction_de_rapport"
    description: str = (
        "Sauvegarde un rapport humain rédigé par l'agent dans un fichier texte."
    )
    args_schema: Type[BaseModel] = ReportWriterInput

    def _run(self, report_path: str, report_text: str) -> str:
        path = Path(report_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            f.write(report_text)

        return f"Rapport sauvegardé avec succès : {path}"