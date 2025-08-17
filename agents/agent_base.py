
class AgentBase:
    def __init__(self, name, team=None, role='generic'):
        self.name=name
        self.team=team
        self.role=role
        self.state=None
    def _set_state(self,state):
        self.state=state
    def perceive(self,obs):
        return obs
    def decide(self,obs):
        raise NotImplementedError
