from .discrete_server import DiscreteProcessSimulator
from .oil_gas_server import OilAndGasSimulator
from .life_sciences_server import LifeSciencesServer
import threading
import logging

__version__ = "0.3.0"
__author__ = "Ben Duran"
__all__ = ["run", "OilAndGasSimulator", "LifeSciencesServer"]

logger = logging.getLogger("SimulatorRunner")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s"))
logger.addHandler(handler)

# --- Registry of all available simulators ---
SIMULATORS = {
    "oil": OilAndGasSimulator,
    "life": LifeSciencesServer,
    "discrete": DiscreteProcessSimulator,
}


def run(mode: str = "oil"):
    """
    Run one or more simulators.

    Args:
        mode (str): one of:
            - "oil"
            - "life"
            - "all" → runs all registered simulators in parallel
    """

    def start_simulator(sim_instance):
        sim_instance.simulate()

    mode = mode.lower()

    if mode in SIMULATORS:
        sim = SIMULATORS[mode]()
        sim.simulate()

    elif mode == "all":
        threads = []
        for name, cls in SIMULATORS.items():
            sim = cls()
            thread = threading.Thread(target=start_simulator, args=(sim,), daemon=True)
            thread.start()
            threads.append(thread)
            logger.info(f"Started simulator: {name}")

        logger.info("All simulators are running. Press Ctrl+C to stop.")
        try:
            while True:
                pass  # Keep main thread alive
        except KeyboardInterrupt:
            logger.info("Simulation interrupted by user. Exiting...")

    else:
        raise ValueError(
            f"Unknown mode: '{mode}'. Must be one of: {list(SIMULATORS.keys()) + ['all']}"
        )
