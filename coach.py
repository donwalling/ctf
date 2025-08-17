
import os, json

def _load_config(path: str):
    cfg = {}
    try:
        import yaml  # optional
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                cfg = yaml.safe_load(f) or {}
    except Exception:
        cfg = {}
    return cfg

def _summarize_log_for_prompt(log: dict) -> str:
    teams = ', '.join(log.get('teams', []))
    outcome = log.get('outcome', {})
    winner = outcome.get('winner', 'N/A')
    score = outcome.get('score', {})
    evs = log.get('recent_events') or log.get('events') or []
    lines = []
    for e in evs[:60]:
        tick = e.get('tick', '?')
        agent = e.get('agent', '?')
        kind = e.get('type') or e.get('action')
        if kind == 'tag':
            lines.append(f"t{tick}: {agent} tagged {e.get('target','?')}")
        elif kind == 'pickup_flag':
            lines.append(f"t{tick}: {agent} picked up the flag")
        elif kind == 'capture':
            lines.append(f"t{tick}: {agent} captured")
        else:
            lines.append(f"t{tick}: {agent} -> {kind}")
    events_text = '\n'.join(lines) if lines else '(no events recorded)'
    return f"""Teams: {teams}
Winner: {winner}
Final Scores: {json.dumps(score)}
Key Events:
{events_text}
"""

def coach_with_llm(log: dict, config_path: str = 'config.yaml') -> str:
    cfg = _load_config(config_path)
    api_key = os.getenv('OPENAI_API_KEY') or cfg.get('openai_api_key')
    model = cfg.get('model', 'gpt-4o-mini')
    if not api_key:
        return ('[coach] Missing API key. Set OPENAI_API_KEY or put openai_api_key in config.yaml.')
    system_msg = (
        "You are a tactical coach for multi-agent capture-the-flag. "
        "Analyze logs and provide concise, actionable feedback. "
        "Focus on roles (scout/attacker/defender), routes, escorts, base defense, and counterplays. "
        "Return a short numbered list of recommendations and one drill."
    )
    user_msg = _summarize_log_for_prompt(log)

    # Preferred: new SDK chat.completions
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg},
                ],
                temperature=0.3,
                max_tokens=700,
            )
            return resp.choices[0].message.content.strip()
        except Exception:
            # Fallback: Responses API
            try:
                resp = client.responses.create(
                    model=model,
                    input=[
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": user_msg},
                    ],
                    temperature=0.3,
                    max_output_tokens=700,
                )
                out = []
                for item in getattr(resp, "output", []) or []:
                    if getattr(item, "type", "") == "message":
                        for content in getattr(item, "content", []) or []:
                            if getattr(content, "type", "") == "text":
                                out.append(content.text)
                return "\n".join(out).strip() if out else "[coach] Empty response."
            except Exception:
                pass
    except Exception:
        pass

    # Legacy fallback
    try:
        import openai
        openai.api_key = api_key
        resp = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "system", "content": system_msg},
                      {"role": "user", "content": user_msg}],
            temperature=0.3,
            max_tokens=700,
        )
        return resp["choices"][0]["message"]["content"].strip()
    except Exception as e3:
        return f"[coach] Unable to call OpenAI API: {e3}"
