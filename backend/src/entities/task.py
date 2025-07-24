from dataclasses import dataclass, asdict
from typing import Dict, Any
import time
from uuid import UUID
from enum import Enum

class TaskType(Enum):
    RESUME_PARSING = "resume_parsing"
    EXTERNAL_ENRICHMENT = "external_enrichment"

@dataclass
class Task:
    candidate_id: str
    task_type: TaskType
    payload: Dict[str, Any]
    created_at: float = time.time()
    retry_count: int = 0

    def to_dict(self):
        task_dict = asdict(self)
        task_dict["task_type"] = self.task_type.value  # Serialize Enum to string
        return task_dict
