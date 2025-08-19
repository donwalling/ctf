
import argparse
from ctf.arena import Arena
from ctf.teams.team_alpha import Team as TeamAlpha
from ctf.teams.team_bravo import Team as TeamBravo
import json, os

def tournament(num_matches=3):
    teams=[TeamAlpha(),TeamBravo()]
    os.makedirs("logs",exist_ok=True)
    results=[]
    for i in range(num_matches):
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

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--num-matches", type=int, default=3)
    args = p.parse_args()
    tournament(num_matches=args.num_matches)

if __name__ == "__main__":
    main()