
import time, copy, random
from .map_loader import load_map, simple_map
from .game_objects import Flag, AgentState
from .scoreboard import Scoreboard
from .events import in_bounds, DIRECTIONS

class Arena:
    def __init__(self, map_spec=None, rows=None, cols=None, teams=None, config=None):
        if isinstance(map_spec, str):
            data = load_map(map_spec)
        elif isinstance(map_spec, dict):
            data = map_spec
        else:
            data = simple_map()
        self.rows = data['rows']
        self.cols = data['cols']
        self.grid = data['grid']
        self.flags = {team: Flag(team, tuple(loc)) for team, loc in data['flags'].items()}
        self.teams = teams or []
        self.agents = []
        self.scoreboard = Scoreboard()
        self.max_turns = 200 if not config else int(config.get('max_turns', 200))
        self.turn = 0
        self._last_event = None
        self._place_agents()

    def _place_agents(self):
        start_positions = {'Team Alpha': (4,2), 'Team Bravo': (4,12)}
        for team in self.teams:
            for i, agent in enumerate(team.agents):
                pos = (start_positions[team.name][0] + (i-1), start_positions[team.name][1] + (i%2))
                state = AgentState(agent.name, team.name, agent.role, pos)
                agent._set_state(state)
                self.agents.append(agent)
                self.scoreboard.ensure_team(team.name)

    def run(self, verbose=False):
        self.turn = 0
        while self.turn < self.max_turns:
            self.turn += 1
            actions = []
            for agent in list(self.agents):
                if not agent.state.alive:
                    continue
                obs = self._observe_for(agent)
                act = agent.decide(obs)
                actions.append((agent, act))
            random.shuffle(actions)
            for agent, act in actions:
                self._apply_action(agent, act)

            self._auto_pickup_flags()
            self._resolve_flag_conditions()
            if verbose:
                self.render()
                time.sleep(0.02)
        return {'scores': self.scoreboard.snapshot(), 'turns': self.turn}

    def _observe_for(self, agent):
        vis = []
        r0,c0 = agent.state.position
        for r in range(max(0,r0-3), min(self.rows, r0+4)):
            row=[]
            for c in range(max(0,c0-3), min(self.cols, c0+4)):
                row.append(self.grid[r][c])
            vis.append(row)

        teammates=[]
        enemies=[]
        friendly_carriers=[]
        enemy_carriers=[]
        for other in self.agents:
            if other is agent:
                continue
            dist = abs(other.state.position[0]-r0)+abs(other.state.position[1]-c0)
            if dist <= 3:
                if other.state.team==agent.state.team:
                    teammates.append((other.state.name, other.state.position))
                    if other.state.has_flag:
                        friendly_carriers.append((other.state.name, other.state.position))
                else:
                    enemies.append((other.state.name, other.state.position))
                    if other.state.has_flag:
                        enemy_carriers.append((other.state.name, other.state.position))

        flags = {t: f.position for t,f in self.flags.items()}
        return {'self': copy.deepcopy(agent.state), 'visible_map': vis,
                'teammates': teammates, 'enemies': enemies,
                'friendly_carriers': friendly_carriers, 'enemy_carriers': enemy_carriers,
                'flags': flags, 'turn': self.turn}

    def _apply_action(self, agent, action):
        if not action: 
            return
        typ = action[0]
        if typ=='move':
            dr,dc=DIRECTIONS.get(action[1],(0,0))
            r,c = agent.state.position
            new=(r+dr,c+dc)
            if in_bounds(new,self.rows,self.cols) and self.grid[new[0]][new[1]]!='#':
                agent.state.position=new
        elif typ=='pickup_flag':
            for t,flag in self.flags.items():
                if t!=agent.state.team and tuple(flag.position)==tuple(agent.state.position) and flag.taken_by is None:
                    flag.taken_by=agent.state.name
                    agent.state.has_flag=True
                    self._last_event={'type':'pickup_flag','agent':agent.state.name,'team':agent.state.team,'tick':self.turn}
        elif typ=='drop_flag':
            if agent.state.has_flag:
                for t,flag in self.flags.items():
                    if flag.taken_by==agent.state.name:
                        flag.taken_by=None
                        flag.position=agent.state.position
                        agent.state.has_flag=False
        elif typ=='tag':
            target_name=action[1]
            target=next((a for a in self.agents if a.state.name==target_name),None)
            if target and abs(target.state.position[0]-agent.state.position[0])+abs(target.state.position[1]-agent.state.position[1])==1:
                self.scoreboard.add(agent.state.team,1)
                self._last_event={'type':'tag','agent':agent.state.name,'target':target.state.name,'team':agent.state.team,'tick':self.turn}
                if target.state.has_flag:
                    target.state.has_flag=False
                    own_flag = self.flags[target.state.team]
                    own_flag.taken_by=None

    def _auto_pickup_flags(self):
        for agent in self.agents:
            if not agent.state.alive or agent.state.has_flag:
                continue
            for t, flag in self.flags.items():
                if t != agent.state.team and tuple(flag.position)==tuple(agent.state.position) and flag.taken_by is None:
                    flag.taken_by = agent.state.name
                    agent.state.has_flag = True
                    self._last_event={'type':'pickup_flag','agent':agent.state.name,'team':agent.state.team,'tick':self.turn}

    def _resolve_flag_conditions(self):
        for agent in self.agents:
            if agent.state.has_flag:
                my_base=self.flags[agent.state.team]
                if tuple(agent.state.position)==tuple(my_base.position):
                    self.scoreboard.add(agent.state.team,5)
                    self._last_event={'type':'capture','agent':agent.state.name,'team':agent.state.team,'tick':self.turn}
                    for t,flag in self.flags.items():
                        if flag.taken_by==agent.state.name:
                            flag.taken_by=None
                            agent.state.has_flag=False

    def render(self):
        grid = [row[:] for row in self.grid]
        for t,flag in self.flags.items():
            r,c = flag.position
            grid[r][c]='A' if t=='Team Alpha' else 'B'
        for agent in self.agents:
            r,c=agent.state.position
            ch = {'scout':'S','attacker':'T','defender':'D'}.get(agent.state.role, agent.state.name[0].upper())
            grid[r][c]=ch
        print('\n'.join(' '.join(row) for row in grid))
        print('Scores:', self.scoreboard.snapshot())
