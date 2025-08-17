
from .agent_base import AgentBase

def _dir_towards(src, dst):
    (r,c) = src; (tr,tc) = dst
    if tr < r: return ('move','up')
    if tr > r: return ('move','down')
    if tc < c: return ('move','left')
    if tc > c: return ('move','right')
    return None

def _manhattan(a,b): return abs(a[0]-b[0]) + abs(a[1]-b[1])

class AttackerAgent(AgentBase):
    def __init__(self,name,team=None):
        super().__init__(name,team,'attacker')

    def decide(self,obs):
        me = obs['self']
        mypos = me.position
        myteam = me.team
        enemy_team = 'Team Alpha' if myteam=='Team Bravo' else 'Team Bravo'
        my_base = obs['flags'][myteam]
        enemy_flag = obs['flags'][enemy_team]

        # Tag if enemy adjacent
        for en_name, en_pos in obs.get('enemies', []):
            if abs(en_pos[0]-mypos[0]) + abs(en_pos[1]-mypos[1]) == 1:
                return ('tag', en_name)

        # If carrying, head home
        if me.has_flag:
            return _dir_towards(mypos, my_base) or None

        # Escort: move toward friendly carrier, else push to flag
        carriers = obs.get('friendly_carriers', [])
        if carriers:
            target = min(carriers, key=lambda x: _manhattan(mypos, x[1]))
            dist = _manhattan(mypos, target[1])
            if dist > 1:
                return _dir_towards(mypos, target[1])
            else:
                return _dir_towards(mypos, my_base) or None

        if tuple(mypos) == tuple(enemy_flag):
            return ('pickup_flag',)

        return _dir_towards(mypos, enemy_flag) or ('move','right')
