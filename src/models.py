from pydantic import BaseModel


class TIRecord(BaseModel):
    rule_id: int
    name: str
    description: str = ""
    references: list[str] = []
    samples: str = ""
    weight: float = 0.0
    area: str
    types: list[str] = []
    apply: bool = True
    agency: str
    lastStatus: str = "added"
    lastUpdate: str  # YYYY-MM-DD
    user: str
    signatures: list[str] = []
