
from arena.arena import Arena
from teams.team_alpha import Team as TeamAlpha
from teams.team_bravo import Team as TeamBravo
import json, os

if __name__=='__main__':
    teams=[TeamAlpha(),TeamBravo()]
    os.makedirs("logs",exist_ok=True)
    results=[]
    for i in range(3):
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
