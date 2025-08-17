
from dataclasses import dataclass

@dataclass
class Flag:
    team: str
    position: tuple
    taken_by: str | None = None

@dataclass
class AgentState:
    name: str
    team: str
    role: str
    position: tuple
    has_flag: bool = False
    alive: bool = True
