
from .agent_base import AgentBase
import random

def _dir_towards(src, dst):
    (r,c) = src; (tr,tc) = dst
    if tr < r: return ('move','up')
    if tr > r: return ('move','down')
    if tc < c: return ('move','left')
    if tc > c: return ('move','right')
    return None

def _manhattan(a,b): return abs(a[0]-b[0]) + abs(a[1]-b[1])

class DefenderAgent(AgentBase):
    def __init__(self,name,team=None):
        super().__init__(name,team,'defender')
    def decide(self,obs):
        me = obs['self']
        mypos = me.position
        myteam = me.team
        my_base = obs['flags'][myteam]

        # Tag adjacent enemies
        for en_name, en_pos in obs.get('enemies', []):
            if abs(en_pos[0]-mypos[0]) + abs(en_pos[1]-mypos[1]) == 1:
                return ('tag', en_name)

        # Chase enemy carriers if visible
        carriers = obs.get('enemy_carriers', [])
        if carriers:
            target = min(carriers, key=lambda x: _manhattan(mypos, x[1]))
            step = _dir_towards(mypos, target[1])
            if step: return step

        enemies = obs.get('enemies', [])
        if enemies:
            target = min(enemies, key=lambda e: _manhattan(mypos, e[1]))
            step = _dir_towards(mypos, target[1])
            if step: return step

        # Otherwise hover near base
        dist = abs(mypos[0]-my_base[0]) + abs(mypos[1]-my_base[1])
        if dist > 2:
            return _dir_towards(mypos, my_base)
        return random.choice([None, ('move','left'), ('move','right'), ('move','up'), ('move','down')])
