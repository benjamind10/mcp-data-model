from opcua import Server
from datetime import datetime
import random
import time
import logging


# ---------- Logging Setup ----------
logger = logging.getLogger("OilAndGasSimulator")
logger.setLevel(logging.INFO)

stream_handler = logging.StreamHandler()
stream_formatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s")
stream_handler.setFormatter(stream_formatter)

logger.addHandler(stream_handler)


# ---------- Simulator Class ----------
class OilAndGasSimulator:
    def __init__(self, endpoint="opc.tcp://0.0.0.0:4840/oilgas/server/"):
        self.server = Server()
        self.server.set_endpoint(endpoint)
        self.idx = self.server.register_namespace("http://oilgas.simulator")
        self.lines = {}

        self._setup_lines()
        logger.info("Simulator initialized with endpoint: %s", endpoint)

    def _setup_lines(self):
        plant = self.server.nodes.objects.add_object(self.idx, "OilAndGasPlant")

        for i in range(1, 6):  # 5 lines
            line_name = f"Line{i}"
            line = plant.add_object(self.idx, line_name)

            # Pump
            pump = line.add_object(self.idx, "Pump")
            pump_vars = {
                "MotorTemp": pump.add_variable(self.idx, "MotorTemp", 0.0),
                "RPM": pump.add_variable(self.idx, "RPM", 0.0),
                "PumpStatus": pump.add_variable(self.idx, "PumpStatus", "Stopped"),
            }

            # Compressor
            compressor = line.add_object(self.idx, "Compressor")
            compressor_vars = {
                "Pressure": compressor.add_variable(self.idx, "Pressure", 0.0),
                "Vibration": compressor.add_variable(self.idx, "Vibration", 0.0),
                "CompressorStatus": compressor.add_variable(
                    self.idx, "CompressorStatus", "Idle"
                ),
            }

            # Valve Group
            valve_group = line.add_object(self.idx, "ValveGroup")
            valve_vars = {
                "InletValve": valve_group.add_variable(self.idx, "InletValve", True),
                "OutletValve": valve_group.add_variable(self.idx, "OutletValve", True),
            }

            # Flow Sensor
            flow_sensor = line.add_object(self.idx, "FlowSensor")
            flow_vars = {
                "FlowRate": flow_sensor.add_variable(self.idx, "FlowRate", 0.0),
                "TotalizedFlow": flow_sensor.add_variable(
                    self.idx, "TotalizedFlow", 0.0
                ),
            }

            # Combine all vars
            self.lines[line_name] = {
                **pump_vars,
                **compressor_vars,
                **valve_vars,
                **flow_vars,
            }

            for var in self.lines[line_name].values():
                var.set_writable()

        logger.info(
            "Configured %d simulation lines with nested assets.", len(self.lines)
        )

    def simulate(self):
        self.server.start()
        logger.info("OPC UA Server started.")
        try:
            while True:
                for line_name, vars in self.lines.items():
                    # Simulate Pump
                    motor_temp = round(random.uniform(60, 120), 2)
                    rpm = round(random.uniform(1500, 3000), 2)
                    pump_status = random.choice(["Running", "Stopped", "Fault"])

                    vars["MotorTemp"].set_value(motor_temp)
                    vars["RPM"].set_value(rpm)
                    vars["PumpStatus"].set_value(pump_status)

                    # Simulate Compressor
                    pressure = round(random.uniform(80, 130), 2)
                    vibration = round(random.uniform(0.1, 1.5), 2)
                    compressor_status = random.choice(["Idle", "Compressing", "Fault"])

                    vars["Pressure"].set_value(pressure)
                    vars["Vibration"].set_value(vibration)
                    vars["CompressorStatus"].set_value(compressor_status)

                    # Simulate Valves
                    vars["InletValve"].set_value(random.choice([True, False]))
                    vars["OutletValve"].set_value(random.choice([True, False]))

                    # Simulate Flow
                    flow_rate = round(random.uniform(100, 500), 2)
                    totalized = vars["TotalizedFlow"].get_value() + flow_rate

                    vars["FlowRate"].set_value(flow_rate)
                    vars["TotalizedFlow"].set_value(totalized)

                    # Log
                    logger.info(
                        f"{line_name} | FlowRate: {flow_rate:.2f} L/min | Total: {totalized:.2f} | "
                        f"Pump: {pump_status} @ {rpm} RPM / {motor_temp}°C | "
                        f"Compressor: {compressor_status} | Pressure: {pressure} psi | Vibration: {vibration}"
                    )

                time.sleep(2)

        except KeyboardInterrupt:
            logger.info("Simulation manually stopped.")
        finally:
            self.server.stop()
            logger.info("Server shutdown complete.")
