
from .agent_base import AgentBase
import random

def _dir_towards(src, dst):
    (r,c) = src; (tr,tc) = dst
    if tr < r: return ('move','up')
    if tr > r: return ('move','down')
    if tc < c: return ('move','left')
    if tc > c: return ('move','right')
    return None

class ScoutAgent(AgentBase):
    def __init__(self,name,team=None):
        super().__init__(name,team,'scout')
    def decide(self,obs):
        me = obs['self']
        mypos = me.position
        myteam = me.team
        enemy_team = 'Team Alpha' if myteam=='Team Bravo' else 'Team Bravo'
        my_base = obs['flags'][myteam]
        enemy_flag = obs['flags'][enemy_team]

        # Opportunistic tag
        for en_name, en_pos in obs.get('enemies', []):
            if abs(en_pos[0]-mypos[0]) + abs(en_pos[1]-mypos[1]) == 1:
                return ('tag', en_name)

        # If carrying flag, go home
        if me.has_flag:
            return _dir_towards(mypos, my_base)

        # If on enemy flag, pick up
        if tuple(mypos) == tuple(enemy_flag):
            return ('pickup_flag',)

        # Explore with bias toward enemy flag
        if random.random() < 0.7:
            step = _dir_towards(mypos, enemy_flag)
            if step: return step
        return ('move', random.choice(['up','down','left','right']))
