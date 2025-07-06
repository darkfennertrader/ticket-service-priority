"""Fallback that always returns Priority.TBD"""

from app.core.models import Priority
from app.core.ports import PriorityClassifierPort


class TbdPriorityClassifier(PriorityClassifierPort):
    async def classify(self, title: str, description: str) -> Priority:
        return Priority.TBD
