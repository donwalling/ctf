# Capture the Flag — Runnable Workshop

Portions of this software were generated with the help of ChatGPT.

Turnkey CTF exercise featuring:
- Core engine (`arena/`, `agents/`, `teams/`)
- CLI runners (`ctf-sim`, `ctf-tourney`, `ctf-recap`, `ctf-dashboard`, `ctf-bot`, `ctf-eval`)
- Post-game tooling (`recap.py`, `coach_mock.py`)
- Visualizations:
  - **Pygame renderer** (local window) — `ctf-sim --render`
  - **Browser dashboard** — `ctf-dashboard` + `logs/state.json`

## Quickstart
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
# source .venv/bin/activate
pip install -e .[dev]
```

### Run a simulation
```bash
ctf-sim --max-turns 60 --delay 0.2         # ASCII
ctf-sim --render --max-turns 60 --delay 0.15  # Pygame (Space=Pause, N=Step, H=Heatmap, C=Clear)
```

### Tournament
```bash
ctf-tourney -n 5
```

### Dashboard
```bash
ctf-dashboard
# in another terminal:
ctf-sim --max-turns 100 --delay 0.2
# open http://localhost:8008/dashboard/index.html
```

### Bot scaffolder & evaluator
```bash
ctf-bot "Team Delta"   # creates teams/team_delta.py
ctf-eval --teams alpha,bravo,delta --matches 3 --seeds 5 --verbose
```

### Tests (optional)
```bash
pip install pytest
pytest -q
```

## Notes
- Logs are written to `logs/`.
- The starter agents are intentionally simple but score naturally (tag=+1, capture=+5).
- Renderer and dashboard are optional; you can run ASCII-only sims.


## LLM Coach
**Online (OpenAI):**
1. `pip install openai`
2. Set your key:
   - PowerShell: `$env:OPENAI_API_KEY="sk-..."`
   - Bash: `export OPENAI_API_KEY="sk-..."`
   - or edit `config.yaml`
3. Run:
```bash
ctf-sim --max-turns 80 --delay 0.15
ctf-coach logs/simulation.json
# or ctf-coach logs/simulation.json --config config.yaml
```

**Offline:**
```bash
ctf-coach-mock logs/simulation.json
```
