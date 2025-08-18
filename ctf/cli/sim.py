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
    sim_mod.simulate(render=a.render, max_turns=a.max_turns, delay=a.delay)

if __name__ == "__main__":
    main()
