from opcua import Server
import random
import time
import logging

# ---------- Logging ----------
logger = logging.getLogger("DiscreteSimulator")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s"))
logger.addHandler(handler)


class DiscreteProcessSimulator:
    def __init__(self, endpoint="opc.tcp://0.0.0.0:4842/discrete/server/"):
        self.server = Server()
        self.server.set_endpoint(endpoint)
        self.idx = self.server.register_namespace("http://discrete.simulator")
        self.lines = {}

        self._setup_lines()
        logger.info("Discrete Process Simulator initialized at %s", endpoint)

    def _setup_lines(self):
        factory = self.server.nodes.objects.add_object(self.idx, "BoardDeckAssembly")

        for i in range(1, 6):
            line_name = f"AssemblyLine{i}"
            line = factory.add_object(self.idx, line_name)

            # Loader
            loader = line.add_object(self.idx, "Loader")
            loader_vars = {
                "BoardPresent": loader.add_variable(self.idx, "BoardPresent", False)
            }

            # Router
            router = line.add_object(self.idx, "Router")
            router_vars = {
                "SpindleSpeed": router.add_variable(self.idx, "SpindleSpeed", 0.0),
                "FeedRate": router.add_variable(self.idx, "FeedRate", 0.0),
                "OperationStatus": router.add_variable(
                    self.idx, "OperationStatus", "Idle"
                ),
            }

            # Press
            press = line.add_object(self.idx, "Press")
            press_vars = {
                "Pressure": press.add_variable(self.idx, "Pressure", 0.0),
                "Temperature": press.add_variable(self.idx, "Temperature", 0.0),
                "PressCycleTime": press.add_variable(self.idx, "PressCycleTime", 0.0),
            }

            # Inspection Station
            inspect = line.add_object(self.idx, "InspectionStation")
            inspect_vars = {
                "SurfaceQuality": inspect.add_variable(
                    self.idx, "SurfaceQuality", "Unknown"
                ),
                "DimensionsOK": inspect.add_variable(self.idx, "DimensionsOK", True),
            }

            # Conveyor
            conveyor = line.add_object(self.idx, "Conveyor")
            conveyor_vars = {"Speed": conveyor.add_variable(self.idx, "Speed", 0.0)}

            self.lines[line_name] = {
                **loader_vars,
                **router_vars,
                **press_vars,
                **inspect_vars,
                **conveyor_vars,
            }

            for var in self.lines[line_name].values():
                var.set_writable()

        logger.info("Configured 5 board deck assembly lines.")

    def simulate(self):
        self.server.start()
        logger.info("Discrete Process OPC UA Server started.")
        try:
            while True:
                for line_name, vars in self.lines.items():
                    # Loader
                    board_present = random.choice([True, False])
                    vars["BoardPresent"].set_value(board_present)

                    # Router
                    operation_status = random.choice(["Idle", "Routing", "Error"])
                    spindle_speed = (
                        random.uniform(5000, 20000)
                        if operation_status == "Routing"
                        else 0
                    )
                    feed_rate = (
                        random.uniform(0.5, 2.5) if operation_status == "Routing" else 0
                    )

                    vars["OperationStatus"].set_value(operation_status)
                    vars["SpindleSpeed"].set_value(round(spindle_speed, 2))
                    vars["FeedRate"].set_value(round(feed_rate, 2))

                    # Press
                    vars["Pressure"].set_value(round(random.uniform(50, 120), 2))
                    vars["Temperature"].set_value(round(random.uniform(100, 180), 2))
                    vars["PressCycleTime"].set_value(round(random.uniform(2.0, 5.0), 2))

                    # Inspection
                    surface_quality = random.choice(
                        ["Excellent", "Good", "Fair", "Fail"]
                    )
                    dims_ok = surface_quality != "Fail"
                    vars["SurfaceQuality"].set_value(surface_quality)
                    vars["DimensionsOK"].set_value(dims_ok)

                    # Conveyor
                    vars["Speed"].set_value(round(random.uniform(0.1, 1.5), 2))

                    logger.info(
                        f"{line_name} | Router: {operation_status} @ {spindle_speed:.0f} RPM | "
                        f"Inspection: {surface_quality} | Conveyor: {vars['Speed'].get_value():.2f} m/s"
                    )

                time.sleep(2)
        except KeyboardInterrupt:
            logger.info("Simulation stopped by user.")
        finally:
            self.server.stop()
            logger.info("Discrete Process Server shutdown complete.")
