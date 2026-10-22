"""允许：PYTHONPATH=src python -m agent …"""

from agent.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
