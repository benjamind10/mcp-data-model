from opcua import Server
import random
import time
import logging

# ---------- Logging ----------
logger = logging.getLogger("LifeSciencesSimulator")
logger.setLevel(logging.INFO)

stream_handler = logging.StreamHandler()
stream_formatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s")
stream_handler.setFormatter(stream_formatter)
logger.addHandler(stream_handler)


class LifeSciencesServer:
    def __init__(self, endpoint="opc.tcp://0.0.0.0:4841/lifesciences/server/"):
        self.server = Server()
        self.server.set_endpoint(endpoint)
        self.idx = self.server.register_namespace("http://lifesciences.simulator")
        self.rooms = {}

        self._setup_rooms()
        logger.info("Life Sciences Simulator initialized at: %s", endpoint)

    def _setup_rooms(self):
        facility = self.server.nodes.objects.add_object(
            self.idx, "LifeSciencesFacility"
        )

        for i in range(1, 11):
            room_name = f"ProcessRoom{i}"
            room = facility.add_object(self.idx, room_name)

            # Bioreactor
            bioreactor = room.add_object(self.idx, "Bioreactor")
            bio_vars = {
                "pH": bioreactor.add_variable(self.idx, "pH", 7.0),
                "DissolvedO2": bioreactor.add_variable(self.idx, "DissolvedO2", 95.0),
                "Temperature": bioreactor.add_variable(self.idx, "Temperature", 37.0),
                "AgitationSpeed": bioreactor.add_variable(
                    self.idx, "AgitationSpeed", 100.0
                ),
            }

            # Centrifuge
            centrifuge = room.add_object(self.idx, "Centrifuge")
            cent_vars = {
                "RPM": centrifuge.add_variable(self.idx, "RPM", 0.0),
                "Status": centrifuge.add_variable(self.idx, "Status", "Idle"),
                "LoadPercent": centrifuge.add_variable(self.idx, "LoadPercent", 0.0),
            }

            # Environment Monitor
            env = room.add_object(self.idx, "EnvironmentMonitor")
            env_vars = {
                "RoomTemp": env.add_variable(self.idx, "RoomTemp", 20.0),
                "Humidity": env.add_variable(self.idx, "Humidity", 50.0),
                "ParticleCount": env.add_variable(self.idx, "ParticleCount", 100),
            }

            # Batch Controller
            batch = room.add_object(self.idx, "BatchController")
            batch_vars = {
                "BatchID": batch.add_variable(self.idx, "BatchID", f"BATCH-{i:03}"),
                "Step": batch.add_variable(self.idx, "Step", "Initialization"),
                "BatchStatus": batch.add_variable(self.idx, "BatchStatus", "Running"),
            }

            self.rooms[room_name] = {**bio_vars, **cent_vars, **env_vars, **batch_vars}

            for var in self.rooms[room_name].values():
                var.set_writable()

        logger.info("Configured 5 Process Rooms with simulated assets.")

    def simulate(self):
        self.server.start()
        logger.info("Life Sciences OPC UA Server started.")
        try:
            while True:
                for room_name, vars in self.rooms.items():
                    # Bioreactor Simulation
                    vars["pH"].set_value(round(random.uniform(6.5, 7.5), 2))
                    vars["DissolvedO2"].set_value(round(random.uniform(80, 100), 2))
                    vars["Temperature"].set_value(round(random.uniform(36, 38), 2))
                    vars["AgitationSpeed"].set_value(round(random.uniform(80, 150), 2))

                    # Centrifuge Simulation
                    status = random.choice(["Idle", "Spinning", "Completed"])
                    rpm = (
                        round(random.uniform(0, 5000), 0) if status == "Spinning" else 0
                    )
                    load = round(random.uniform(10, 90), 2) if status != "Idle" else 0.0

                    vars["RPM"].set_value(rpm)
                    vars["Status"].set_value(status)
                    vars["LoadPercent"].set_value(load)

                    # Environmental Conditions
                    vars["RoomTemp"].set_value(round(random.uniform(19.5, 21.0), 2))
                    vars["Humidity"].set_value(round(random.uniform(45, 55), 2))
                    vars["ParticleCount"].set_value(random.randint(80, 150))

                    # Batch Controller Simulation
                    vars["Step"].set_value(
                        random.choice(
                            ["Initialization", "Mixing", "Filling", "Completed"]
                        )
                    )
                    vars["BatchStatus"].set_value(
                        random.choice(["Running", "Paused", "Error", "Completed"])
                    )

                    logger.info(
                        f"{room_name} | Bioreactor pH: {vars['pH'].get_value()} | "
                        f"Centrifuge: {status} @ {rpm} RPM | "
                        f"Env: Temp {vars['RoomTemp'].get_value()}°C, "
                        f"Humidity {vars['Humidity'].get_value()}%, Particles {vars['ParticleCount'].get_value()}"
                    )

                time.sleep(2)
        except KeyboardInterrupt:
            logger.info("Simulation manually stopped.")
        finally:
            self.server.stop()
            logger.info("Life Sciences Server shutdown complete.")
