
import argparse, os, time, json, sys, re, pathlib, importlib

from ctf.arena import Arena
from ctf.teams.team_alpha import Team as TeamAlpha
from ctf.teams.team_bravo import Team as TeamBravo

def _clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def sim_main():
    p = argparse.ArgumentParser(description="Run a CTF simulation")
    p.add_argument("--max-turns", type=int, default=60)
    p.add_argument("--delay", type=float, default=0.2)
    p.add_argument("--render", action="store_true", help="Use Pygame renderer")
    args = p.parse_args()

    teams = [TeamAlpha(), TeamBravo()]
    arena = Arena(teams=teams)
    os.makedirs("logs", exist_ok=True)
    log_events = []

    if args.render:
        try:
            from renderer import run_pygame_loop
        except Exception as e:
            print("Renderer unavailable. Install pygame and ensure renderer.py exists.", e)
            sys.exit(1)

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

            snap = {
                "turn": turn,
                "teams": [t.name for t in teams],
                "scores": arena.scoreboard.snapshot(),
                "flags": {team: {"position": list(flag.position), "taken_by": flag.taken_by} for team, flag in arena.flags.items()},
                "agents": [{"name": a.state.name, "team": a.state.team, "role": a.state.role,
                            "position": list(a.state.position), "has_flag": a.state.has_flag, "alive": a.state.alive}
                           for a in arena.agents]
            }
            with open("logs/state.json","w") as f:
                json.dump(snap, f)
        run_pygame_loop(arena, step_once, max_turns=args.max_turns, delay=args.delay)
    else:
        for turn in range(1, args.max_turns+1):
            _clear()
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
            time.sleep(args.delay)

    print("\n\N{CHEQUERED FLAG} Simulation Complete!")
    print("Final Scores:", arena.scoreboard.snapshot())

    outcome_scores = arena.scoreboard.snapshot()
    winner = max(outcome_scores, key=outcome_scores.get) if outcome_scores else "N/A"
    log_data = {"teams": [team.name for team in teams],
                "outcome": {"score": outcome_scores, "winner": winner},
                "events": log_events}
    with open("logs/simulation.json", "w") as f:
        json.dump(log_data, f, indent=2)
    print("\N{OPEN FILE FOLDER} Simulation log saved to 'logs/simulation.json'")

def tourney_main():
    p = argparse.ArgumentParser(description="Run a CTF tournament (N matches)")
    p.add_argument("-n", "--num-matches", type=int, default=3)
    args = p.parse_args()

    os.makedirs("logs", exist_ok=True)
    teams=[TeamAlpha(),TeamBravo()]
    results=[]
    for i in range(args.num_matches):
        arena=Arena(teams=teams)
        res=arena.run(verbose=False)
        print(f"Match {i+1} scores: {res['scores']}")
        winner=max(res['scores'],key=res['scores'].get) if res['scores'] else "N/A"
        log_file=f"logs/match_{i+1}.json"
        json.dump({
            "teams":[t.name for t in teams],
            "outcome":{"score":res['scores'],"winner":winner},
            "events":[]
        }, open(log_file,"w"), indent=2)
        results.append(res)
    final={}
    for r in results:
        for t,s in r['scores'].items():
            final[t]=final.get(t,0)+s
    print('Final aggregate scores:', final)

def recap_main():
    p = argparse.ArgumentParser(description="Recap a simulation/tournament log")
    p.add_argument("logfile")
    args = p.parse_args()
    with open(args.logfile,"r") as f:
        data=json.load(f)
    print("=== Simulation Recap ===")
    print(f"Teams: {', '.join(data.get('teams', []))}")
    out=data.get('outcome',{})
    print(f"Winner: {out.get('winner','N/A')}")
    print(f"Final Scores: {out.get('score', {})}")
    ev=data.get('events',[])[:15]
    if ev:
        print("\nKey Events (first 15):")
        for e in ev:
            print(f"Turn {e.get('tick','?')}: {e.get('agent','?')} -> {e.get('action','?')}")


def coach_main():
    p = argparse.ArgumentParser(description="LLM coaching on a log")
    p.add_argument("logfile")
    p.add_argument("--config", default="config.yaml")
    args = p.parse_args()
    with open(args.logfile, "r", encoding="utf-8") as f:
        log = json.load(f)
    try:
        import coach
        out = coach.coach_with_llm(log, config_path=args.config)
        print(out)
    except Exception as e:
        print("[coach] Failed to run LLM coach:", e)
        print("Try: pip install openai and set OPENAI_API_KEY or update config.yaml")


def coach_mock_main():
    p = argparse.ArgumentParser(description="Mock coaching on a log")
    p.add_argument("logfile")
    args = p.parse_args()
    with open(args.logfile,"r") as f:
        log=json.load(f)
    try:
        import coach_mock as cm
        print(cm.coach_mock(log))
    except Exception as e:
        print("[coach_mock] Failed to run mock coach:", e)

def dashboard_main():
    from dashboard_server import main as serve
    serve()

# ---- Bot scaffolder ----
def bot_init_team_main():
    p = argparse.ArgumentParser(description="Scaffold a new team")
    p.add_argument("name", help="Team name, e.g., 'Team Delta' or 'Delta'")
    args = p.parse_args()

    raw = args.name.strip()
    m = re.sub(r"^team\s+", "", raw, flags=re.I)
    m = re.sub(r"\s+", "_", m.strip().lower())
    module_name = f"team_{m}"
    team_display = f"Team {m.replace('_',' ').title()}"
    dest = pathlib.Path("teams") / f"{module_name}.py"
    dest.parent.mkdir(parents=True, exist_ok=True)

    if dest.exists():
        print(f"[init-team] {dest} already exists. Aborting.")
        return

    template = f"""
from ctf.agents.agent_scout import ScoutAgent
from ctf.agents.agent_attacker import AttackerAgent
from ctf.agents.agent_defender import DefenderAgent

class Team:
    def __init__(self):
        self.name='{team_display}'
        self.agents=[
            ScoutAgent('{m}_scout', self.name),
            AttackerAgent('{m}_att', self.name),
            DefenderAgent('{m}_def', self.name)
        ]
""".lstrip()

    dest.write_text(template, encoding="utf-8")
    print(f"[init-team] Created {dest}")

# ---- Evaluator ----
def _load_team_ctor(mod_name: str):
    slug = re.sub(r"^team\s+", "", mod_name, flags=re.I)
    slug = slug.strip().lower().replace(" ", "_")
    if not slug:
        raise ValueError("Empty team name")
    if not slug.startswith("team_"):
        slug = f"team_{slug}"
    module_path = f"teams.{slug}"
    mod = importlib.import_module(module_path)
    if not hasattr(mod, "Team"):
        raise ImportError(f"{module_path} missing Team class")
    return getattr(mod, "Team"), slug

def eval_main():
    import random, itertools, time
    p = argparse.ArgumentParser(description="Round-robin evaluator for multiple teams across seeds")
    p.add_argument("--teams", type=str, default="alpha,bravo",
                   help="Comma-separated team modules or names, e.g., 'alpha,bravo,delta' or 'team_alpha,team_bravo'")
    p.add_argument("--matches", type=int, default=3, help="Matches per pairing per seed")
    p.add_argument("--seeds", type=int, default=3, help="Number of seeds to try (0..seeds-1)")
    p.add_argument("--verbose", action="store_true")
    args = p.parse_args()

    team_tokens = [t.strip() for t in args.teams.split(",") if t.strip()]
    if len(team_tokens) < 2:
        print("[ctf-eval] Need at least 2 teams"); return

    ctors = []
    for t in team_tokens:
        ctor, slug = _load_team_ctor(t)
        ctors.append((ctor, slug))

    totals = {slug: 0 for _, slug in ctors}
    wins = {slug: 0 for _, slug in ctors}
    ties = 0

    pairs = list(itertools.combinations(ctors, 2))
    os.makedirs("logs", exist_ok=True)
    run_id = int(time.time())

    idx = 0
    for seed in range(args.seeds):
        random.seed(seed)
        for (ctorA, slugA), (ctorB, slugB) in pairs:
            for m in range(args.matches):
                idx += 1
                teams = [ctorA(), ctorB()]
                arena = Arena(teams=teams)
                res = arena.run(verbose=False)
                score = res.get("scores", {})
                a_score = score.get(teams[0].name, 0)
                b_score = score.get(teams[1].name, 0)
                totals[slugA] += a_score
                totals[slugB] += b_score
                if a_score > b_score:
                    wins[slugA] += 1
                elif b_score > a_score:
                    wins[slugB] += 1
                else:
                    ties += 1

                log_file=f"logs/eval_{run_id}_{idx:03d}.json"
                with open(log_file, "w") as f:
                    json.dump({
                        "seed": seed,
                        "pair": [slugA, slugB],
                        "scores": score,
                        "turns": res.get("turns")
                    }, f, indent=2)
                if args.verbose:
                    print(f"[{idx}] seed={seed} {slugA} vs {slugB} -> {score}")

    print("\n=== EVAL SUMMARY ===")
    print("Teams:", ", ".join(slug for _, slug in ctors))
    print("Total scores:")
    for _, slug in ctors:
        print(f"  {slug:>12}: {totals[slug]}  (wins: {wins[slug]})")
    print(f"Ties: {ties}")
