from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict, Optional

import requests

from .config import get_settings

settings = get_settings()


class ComfyClient:
    def __init__(self, base_url: Optional[str] = None) -> None:
        self.base_url = (base_url or settings.comfy_base_url).rstrip("/")
        self.output_dir = Path(settings.comfy_output_dir)

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def system_stats(self) -> Dict[str, Any]:
        r = requests.get(self._url("/system_stats"), timeout=15)
        r.raise_for_status()
        return r.json()

    def object_info(self) -> Dict[str, Any]:
        r = requests.get(self._url("/object_info"), timeout=30)
        r.raise_for_status()
        return r.json()

    def queue(self) -> Dict[str, Any]:
        r = requests.get(self._url("/queue"), timeout=15)
        r.raise_for_status()
        return r.json()

    def history(self) -> Dict[str, Any]:
        r = requests.get(self._url("/history"), timeout=30)
        r.raise_for_status()
        return r.json()

    def available_checkpoints(self) -> list[str]:
        data = self.object_info()
        return data["CheckpointLoaderSimple"]["input"]["required"]["ckpt_name"][0]

    def build_image_workflow(
        self,
        *,
        prompt: str,
        negative_prompt: str,
        width: int,
        height: int,
        steps: int,
        cfg: float,
        seed: int,
        checkpoint_name: str,
        filename_prefix: str,
    ) -> Dict[str, Any]:
        return {
            "1": {
                "inputs": {"ckpt_name": checkpoint_name},
                "class_type": "CheckpointLoaderSimple",
            },
            "2": {
                "inputs": {"text": prompt, "clip": ["1", 1]},
                "class_type": "CLIPTextEncode",
            },
            "3": {
                "inputs": {"text": negative_prompt, "clip": ["1", 1]},
                "class_type": "CLIPTextEncode",
            },
            "4": {
                "inputs": {"width": width, "height": height, "batch_size": 1},
                "class_type": "EmptyLatentImage",
            },
            "5": {
                "inputs": {
                    "seed": seed,
                    "steps": steps,
                    "cfg": cfg,
                    "sampler_name": settings.comfy_default_sampler,
                    "scheduler": settings.comfy_default_scheduler,
                    "denoise": 1,
                    "model": ["1", 0],
                    "positive": ["2", 0],
                    "negative": ["3", 0],
                    "latent_image": ["4", 0],
                },
                "class_type": "KSampler",
            },
            "6": {
                "inputs": {"samples": ["5", 0], "vae": ["1", 2]},
                "class_type": "VAEDecode",
            },
            "7": {
                "inputs": {"filename_prefix": filename_prefix, "images": ["6", 0]},
                "class_type": "SaveImage",
            },
        }

    def submit_prompt(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        r = requests.post(self._url("/prompt"), json={"prompt": workflow}, timeout=30)
        r.raise_for_status()
        return r.json()

    def wait_for_prompt(self, prompt_id: str, timeout_seconds: int = 300) -> Dict[str, Any]:
        started = time.time()
        while time.time() - started < timeout_seconds:
            history = self.history()
            if prompt_id in history:
                return history[prompt_id]
            time.sleep(2)
        raise TimeoutError(f"Prompt nicht fertig: {prompt_id}")

    def resolve_output_file(self, history_item: Dict[str, Any]) -> Optional[Path]:
        outputs = history_item.get("outputs", {})
        for node_data in outputs.values():
            images = node_data.get("images", [])
            if not images:
                continue
            image = images[0]
            filename = image.get("filename")
            subfolder = image.get("subfolder", "")
            p = self.output_dir / subfolder / filename
            if p.exists():
                return p
        return None
