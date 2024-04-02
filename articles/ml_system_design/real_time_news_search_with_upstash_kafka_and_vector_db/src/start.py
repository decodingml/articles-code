"""
    This script represents the Bytewax Flow entrypoint.
    To be ran with: poetry run python -m bytewax.run start:flow
"""

from bytewax.testing import run_main
from flow import build as build_flow

flow = build_flow()

if __name__ == "__main__":
    run_main(flow)
