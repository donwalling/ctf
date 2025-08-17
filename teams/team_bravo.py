
from agents.agent_scout import ScoutAgent
from agents.agent_attacker import AttackerAgent
from agents.agent_defender import DefenderAgent

class Team:
    def __init__(self):
        self.name='Team Bravo'
        self.agents=[
            ScoutAgent('bravo_scout', self.name),
            AttackerAgent('bravo_att', self.name),
            DefenderAgent('bravo_def', self.name)
        ]
