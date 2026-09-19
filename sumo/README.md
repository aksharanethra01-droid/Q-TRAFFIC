# SUMO corridor

This directory contains a real four-intersection SUMO corridor, route demand, traffic-light programs, and TraCI controller.

If `SUMO_HOME` is configured, `python build_network.py` can regenerate `network.net.xml` from the node/edge source files. `run_sumo.py` uses SUMO/TraCI directly and never substitutes a Python traffic mock when SUMO is unavailable.
