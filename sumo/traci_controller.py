import os
import shutil
from pathlib import Path


class SumoUnavailable(RuntimeError):
    pass


def find_sumo(binary="sumo"):

    # 1. Check PATH
    for name in (binary, binary + ".exe"):

        found = shutil.which(name)

        if found:
            return found

    # 2. Check SUMO_HOME
    sumo_home = os.environ.get("SUMO_HOME")

    if sumo_home:

        candidate = (
            Path(sumo_home)
            / "bin"
            / (binary + ".exe")
        )

        if candidate.exists():
            return str(candidate)

    # 3. Default Windows installation
    common_path = (
        Path(r"C:\Program Files (x86)\Eclipse\Sumo\bin")
        / (binary + ".exe")
    )

    if common_path.exists():
        return str(common_path)

    raise SumoUnavailable(
        "SUMO is not installed/configured. "
        "Set SUMO_HOME or add SUMO bin to PATH."
    )


class TraCIController:

    def __init__(
        self,
        config_file=None,
        gui=False,
        seed=7
    ):

        self.base = Path(__file__).resolve().parent

        self.config_file = Path(
            config_file
            or self.base / "scenario.sumo.cfg"
        )

        self.gui = gui
        self.seed = seed
        self.traci = None

    # =========================================================
    # START SUMO
    # =========================================================

    def start(self):

        binary = find_sumo(
            "sumo-gui" if self.gui else "sumo"
        )

        try:

            import traci

        except Exception as exc:

            raise SumoUnavailable(
                f"TraCI Python package is unavailable: {exc}"
            )

        self.traci = traci

        command = [
            binary,
            "-c",
            str(self.config_file),
            "--seed",
            str(self.seed),
        ]

        self.traci.start(command)

        print("SUMO + TraCI started successfully")

    # =========================================================
    # SIMULATION STEP
    # =========================================================

    def simulation_step(self):

        self.traci.simulationStep()

    # =========================================================
    # VEHICLE COUNT
    # =========================================================

    def vehicle_count(self):

        return len(
            self.traci.vehicle.getIDList()
        )

    # =========================================================
    # WAITING TIME
    # =========================================================

    def waiting_time(self):

        vehicle_ids = (
            self.traci.vehicle.getIDList()
        )

        return sum(
            self.traci.vehicle.getWaitingTime(
                vehicle_id
            )
            for vehicle_id in vehicle_ids
        )

    # =========================================================
    # TRAFFIC LIGHT STATE
    # =========================================================

    def traffic_lights(self):

        return {

            tls:
            self.traci.trafficlight
            .getRedYellowGreenState(tls)

            for tls in
            self.traci.trafficlight
            .getIDList()
        }

    # =========================================================
    # QUEUE INFORMATION
    # =========================================================

    def queue_information(self):

        result = {}

        for tls in (
            self.traci.trafficlight
            .getIDList()
        ):

            lanes = (
                self.traci.trafficlight
                .getControlledLanes(tls)
            )

            result[tls] = {}

            for lane in lanes:

                result[tls][lane] = (
                    self.traci.lane
                    .getLastStepHaltingNumber(
                        lane
                    )
                )

        return result

    # =========================================================
    # CURRENT PHASE
    # =========================================================

    def get_phase(self, junction_id):

        if junction_id not in (
            self.traci.trafficlight
            .getIDList()
        ):

            return None

        return (
            self.traci.trafficlight
            .getPhase(junction_id)
        )

    # =========================================================
    # CURRENT PHASE DURATION
    # =========================================================

    def get_phase_duration(self, junction_id):

        if junction_id not in (
            self.traci.trafficlight
            .getIDList()
        ):

            return None

        return (
            self.traci.trafficlight
            .getPhaseDuration(junction_id)
        )

    # =========================================================
    # ADAPTIVE SIGNAL PLAN
    # =========================================================

    def apply_signal_plan(
        self,
        junction_id,
        plan_name
    ):

        # -----------------------------------------------------
        # Check junction
        # -----------------------------------------------------

        if junction_id not in (
            self.traci.trafficlight
            .getIDList()
        ):

            return False

        # -----------------------------------------------------
        # Candidate green durations
        # -----------------------------------------------------

        plans = {

            "PLAN_1": 30,

            "PLAN_2": 45,

            "PLAN_3": 60,
        }

        if plan_name not in plans:

            return False

        green_duration = plans[plan_name]

        # -----------------------------------------------------
        # IMPORTANT:
        #
        # Phase 0 = GREEN
        # Phase 1 = YELLOW
        # Phase 2 = RED
        #
        # Therefore explicitly move to phase 0.
        # -----------------------------------------------------

        self.traci.trafficlight.setPhase(
            junction_id,
            0
        )

        # -----------------------------------------------------
        # Set selected green duration
        # -----------------------------------------------------

        self.traci.trafficlight.setPhaseDuration(
            junction_id,
            green_duration
        )

        print(
            f"[SIGNAL CONTROL] "
            f"{junction_id} "
            f"-> {plan_name} "
            f"-> GREEN {green_duration}s"
        )

        return True

    # =========================================================
    # FORCE GREEN
    # =========================================================

    def set_green(self, junction_id):

        if junction_id not in (
            self.traci.trafficlight
            .getIDList()
        ):

            return False

        self.traci.trafficlight.setPhase(
            junction_id,
            0
        )

        return True

    # =========================================================
    # FORCE RED
    # =========================================================

    def set_red(self, junction_id):

        if junction_id not in (
            self.traci.trafficlight
            .getIDList()
        ):

            return False

        self.traci.trafficlight.setPhase(
            junction_id,
            2
        )

        return True

    # =========================================================
    # CLOSE SUMO
    # =========================================================

    def close(self):

        if self.traci:

            try:

                self.traci.close()

            finally:

                self.traci = None