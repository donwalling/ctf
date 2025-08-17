
import sys, json

def coach_mock(log):
    lines=["=== MOCK COACH FEEDBACK ==="]
    winner = log.get('outcome',{}).get('winner','N/A')
    lines.append(f"Winner: {winner}")
    for team in log.get('teams',[]):
        if team != winner:
            lines.append(f"Suggestion for {team}: Improve scout-attacker coordination; keep a defender closer to base.")
        else:
            lines.append(f"{team}: Solid performance. Maintain map control and support carriers on return runs.")
    if not log.get('events'):
        lines.append("No events recorded — consider increasing max_turns or improving agent exploration.")
    return "\n".join(lines)

if __name__=="__main__":
    if len(sys.argv)!=2:
        print("Usage: python coach_mock.py logs/simulation.json"); sys.exit(1)
    with open(sys.argv[1],"r") as f:
        log=json.load(f)
    print(coach_mock(log))
