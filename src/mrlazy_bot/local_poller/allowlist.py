from dataclasses import dataclass
from typing import Dict, List, Optional

import yaml


@dataclass
class AllowedCommand:
    exec: str
    fixed_args: List[str]
    working_dir: Optional[str]
    timeout: Optional[int]


class CommandAllowlist:
    def __init__(self, mapping: Dict[str, AllowedCommand]):
        self._mapping = mapping

    @staticmethod
    def load_from_yaml(path: str) -> "CommandAllowlist":
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        commands = data.get("commands") or {}
        mapping: Dict[str, AllowedCommand] = {}
        for name, spec in commands.items():
            mapping[name] = AllowedCommand(
                exec=str(spec.get("exec") or ""),
                fixed_args=list(spec.get("fixed_args") or []),
                working_dir=spec.get("working_dir") or None,
                timeout=spec.get("timeout") or None,
            )
        return CommandAllowlist(mapping)

    def get(self, name: str) -> Optional[AllowedCommand]:
        return self._mapping.get(name)


