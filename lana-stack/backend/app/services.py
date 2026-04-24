from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from sqlmodel import select

from .comfy_client import ComfyClient
from .config import get_settings
from .db import get_session
from .models import Job
from .schemas import ImageGenerateRequest

settings = get_settings()


class RenderService:
    def __init__(self) -> None:
        self.client = ComfyClient()
        self.export_dir = Path(settings.output_local_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def generate_image(self, req: ImageGenerateRequest) -> Job:
        ckpt_name = req.checkpoint_name or settings.comfy_checkpoint
        checkpoints = self.client.available_checkpoints()
        if ckpt_name not in checkpoints:
            raise ValueError(f"Checkpoint nicht gefunden: {ckpt_name}")

        workflow = self.client.build_image_workflow(
            prompt=req.prompt,
            negative_prompt=req.negative_prompt,
            width=req.width,
            height=req.height,
            steps=req.steps,
            cfg=req.cfg,
            seed=req.seed,
            checkpoint_name=ckpt_name,
            filename_prefix=req.filename_prefix,
        )

        response = self.client.submit_prompt(workflow)
        prompt_id = response["prompt_id"]

        with get_session() as session:
            job = Job(
                prompt_id=prompt_id,
                kind="image",
                prompt=req.prompt,
                status="queued",
                meta_json=json.dumps(response),
            )
            session.add(job)
            session.flush()
            session.refresh(job)
            return job

    def finalize_job(self, prompt_id: str) -> Job:
        history_item = self.client.wait_for_prompt(prompt_id)
        output_file = self.client.resolve_output_file(history_item)

        if output_file is None:
            raise FileNotFoundError(f"Keine Output-Datei für {prompt_id}")

        target = self.export_dir / output_file.name
        shutil.copy2(output_file, target)

        with get_session() as session:
            job = session.exec(select(Job).where(Job.prompt_id == prompt_id)).first()
            if job is None:
                raise ValueError(f"Job nicht gefunden: {prompt_id}")

            job.status = "success"
            job.filename = target.name
            job.full_path = str(target)
            job.finished_at = datetime.now(timezone.utc)
            job.meta_json = json.dumps(history_item)
            session.add(job)
            session.flush()
            session.refresh(job)
            return job

    def get_job(self, prompt_id: str) -> Optional[Job]:
        with get_session() as session:
            return session.exec(select(Job).where(Job.prompt_id == prompt_id)).first()
