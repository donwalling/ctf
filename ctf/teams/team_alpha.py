
from ctf.agents.agent_scout import ScoutAgent
from ctf.agents.agent_attacker import AttackerAgent
from ctf.agents.agent_defender import DefenderAgent

class Team:
    def __init__(self):
        self.name='Team Alpha'
        self.agents=[
            ScoutAgent('alpha_scout', self.name),
            AttackerAgent('alpha_att', self.name),
            DefenderAgent('alpha_def', self.name)
        ]
