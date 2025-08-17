
import sys, json

def recap(log_file):
    with open(log_file, 'r') as f:
        data = json.load(f)
    print("=== Simulation Recap ===")
    print(f"Teams: {', '.join(data.get('teams', []))}")
    out = data.get('outcome', {})
    print(f"Winner: {out.get('winner','N/A')}")
    print(f"Final Scores: {out.get('score', {})}")
    print("\nKey Events (first 15):")
    for event in data.get('events', [])[:15]:
        print(f"Turn {event.get('tick','?')}: {event.get('agent','?')} -> {event.get('action','?')}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python recap.py logs/simulation.json")
        sys.exit(1)
    recap(sys.argv[1])
