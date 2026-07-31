from __future__ import annotations

from pathlib import Path
import json

from app.graph.state import AgentState


class CheckpointManager:

    def __init__(

        self,

        checkpoint_dir: str = "storage/checkpoints",

    ):

        self.directory = Path(checkpoint_dir)

        self.directory.mkdir(

            parents=True,

            exist_ok=True,

        )

        def save(

        self,

        workflow_id: str,

        state: AgentState,

    ):

        path = self.directory / f"{workflow_id}.json"

        path.write_text(

            state.model_dump_json(

                indent=2,

            )

        )

    def load(

        self,

        workflow_id: str,

    ) -> AgentState | None:

        path = self.directory / f"{workflow_id}.json"

        if not path.exists():

            return None

        data = json.loads(

            path.read_text()

        )

        return AgentState(

            **data

        
        
        )

    def delete(

        self,

        workflow_id: str,

    ):

        path = self.directory / f"{workflow_id}.json"

        if path.exists():

            path.unlink()