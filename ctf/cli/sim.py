import argparse, importlib, sys

def main() -> None:
    p = argparse.ArgumentParser(prog="ctf-sim", description="Run CTF simulator")
    p.add_argument("--render", action="store_true")
    p.add_argument("--max-turns", type=int, default=100)
    p.add_argument("--delay", type=float, default=0.2)
    a = p.parse_args()

    if a.render:
        try:
            import pygame  # noqa: F401
            from ctf import renderer as _  # noqa: F401
        except Exception:
            sys.stderr.write("Renderer unavailable. Install with: pip install '.[render]'\n")
            raise

    sim_mod = importlib.import_module("ctf.simulate")

    if hasattr(sim_mod, "run"):
        sim_mod.run(render=a.render, max_turns=a.max_turns, delay=a.delay)
    elif hasattr(sim_mod, "main"):
        sim_mod.main(render=a.render, max_turns=a.max_turns, delay=a.delay)
    else:
        sys.stderr.write("ctf.simulate missing run(...) or main(...)\n")
        sys.exit(2)

if __name__ == "__main__":
    main()
