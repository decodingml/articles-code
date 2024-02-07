from bytewax.testing import run_main

from src.flow import build as build_flow

flow = build_flow(in_memory=False)

if __name__ == "__main__":
    run_main(flow)
