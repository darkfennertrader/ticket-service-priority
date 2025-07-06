from app.core.models import Priority
from app.core.ports import PriorityClassifierPort


class FakePriorityClassifier(PriorityClassifierPort):
    """
    Fake Classifier.
    """

    KEYWORDS_HIGH = ("urgent", "asap", "immediately", "fail", "error", "crash")
    KEYWORDS_MEDIUM = ("slow", "delay", "later", "problem")

    async def classify(self, title: str, description: str) -> Priority:
        text = f"{title} {description}".lower()
        if any(w in text for w in self.KEYWORDS_HIGH):
            return Priority.HIGH
        if any(w in text for w in self.KEYWORDS_MEDIUM):
            return Priority.MEDIUM
        return Priority.LOW
