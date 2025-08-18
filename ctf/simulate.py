
import os, time, json, argparse
from ctf.arena import Arena
from ctf.teams.team_alpha import Team as TeamAlpha
from ctf.teams.team_bravo import Team as TeamBravo

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def snapshot(arena, turn, teams, recent_events):
    return {
        "turn": turn,
        "teams": [t.name for t in teams],
        "scores": arena.scoreboard.snapshot(),
        "flags": {team: {"position": list(flag.position), "taken_by": flag.taken_by} for team, flag in arena.flags.items()},
        "agents": [
            {"name": a.state.name, "team": a.state.team, "role": a.state.role,
             "position": list(a.state.position), "has_flag": a.state.has_flag, "alive": a.state.alive}
            for a in arena.agents
        ],
        "recent_events": recent_events[-12:]
    }

def simulate(max_turns=60, delay=0.2, render=False):
    teams = [TeamAlpha(), TeamBravo()]
    arena = Arena(teams=teams)
    os.makedirs("logs", exist_ok=True)
    log_events = []
    recent_events = []

    def note(evt):
        if evt: recent_events.append(evt)

    if render:
        from ctf.renderer import run_pygame_loop
        def step_once(turn):
            actions = []
            for ag in arena.agents:
                if ag.state.alive:
                    obs = arena._observe_for(ag)
                    action = ag.decide(obs)
                    actions.append((ag, action))
                    if action:
                        log_events.append({"tick": turn, "agent": ag.name, "action": action[0], "details": action})
            for ag, action in actions:
                arena._apply_action(ag, action)
            arena._auto_pickup_flags()
            arena._resolve_flag_conditions()

            evt = getattr(arena, "_last_event", None)
            if isinstance(evt, dict) and evt.get("tick")==turn:
                note(evt)

            with open("logs/state.json","w") as f:
                json.dump(snapshot(arena, turn, teams, recent_events), f)

        run_pygame_loop(arena, step_once, max_turns=max_turns, delay=delay)
    else:
        for turn in range(1, max_turns+1):
            clear_console()
            print(f"--- Turn {turn} ---")
            arena.render()

            actions = []
            for ag in arena.agents:
                if ag.state.alive:
                    obs = arena._observe_for(ag)
                    action = ag.decide(obs)
                    actions.append((ag, action))
                    if action:
                        log_events.append({"tick": turn, "agent": ag.name, "action": action[0], "details": action})
            for ag, action in actions:
                arena._apply_action(ag, action)
            arena._auto_pickup_flags()
            arena._resolve_flag_conditions()

            evt = getattr(arena, "_last_event", None)
            if isinstance(evt, dict) and evt.get("tick")==turn:
                note(evt)

            with open("logs/state.json","w") as f:
                json.dump(snapshot(arena, turn, teams, recent_events), f)
            time.sleep(delay)

    print("\n\N{CHEQUERED FLAG} Simulation Complete!")
    print("Final Scores:", arena.scoreboard.snapshot())

    outcome_scores = arena.scoreboard.snapshot()
    winner = max(outcome_scores, key=outcome_scores.get) if outcome_scores else "N/A"
    log_data = {
        "teams": [team.name for team in teams],
        "outcome": {"score": outcome_scores, "winner": winner},
        "events": log_events,
        "recent_events": recent_events[-50:]
    }
    with open("logs/simulation.json", "w") as f:
        json.dump(log_data, f, indent=2)
    print(f"\N{OPEN FILE FOLDER} Simulation log saved to 'logs/simulation.json'")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--max-turns", type=int, default=60)
    p.add_argument("--delay", type=float, default=0.2)
    p.add_argument("--render", action="store_true")
    args = p.parse_args()
    simulate(max_turns=args.max_turns, delay=args.delay, render=args.render)
