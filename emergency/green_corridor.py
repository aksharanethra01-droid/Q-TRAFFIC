from dataclasses import dataclass, field
from typing import List


@dataclass
class GreenCorridorDecision:
    active: bool
    emergency_junction: str
    route: List[str] = field(default_factory=list)
    blocked_junctions: List[str] = field(default_factory=list)
    reason: str = ""
    priority: str = "HIGH"

    @property
    def corridor_status(self):
        if self.active:
            return "ACTIVE"

        if self.blocked_junctions:
            return "BLOCKED"

        return "CLEARED"

    def to_dict(self):
        return {
            "active": self.active,
            "corridor_status": self.corridor_status,
            "emergency_junction": self.emergency_junction,
            "route": self.route,
            "blocked_junctions": self.blocked_junctions,
            "reason": self.reason,
            "priority": self.priority,
        }


class GreenCorridorController:

    def __init__(
        self,
        route=None,
        queue_threshold=0.35,
        occupancy_threshold=0.70,
    ):
        self.route = route or [
            "J1",
            "J2",
            "J3",
            "J4",
        ]

        self.queue_threshold = queue_threshold
        self.occupancy_threshold = occupancy_threshold

        self.active = False
        self.emergency_junction = None
        self.blocked_junctions = []

    def _clearance_ok(self, downstream):
        capacity = max(
            float(
                downstream.get(
                    "capacity",
                    50,
                )
            ),
            1.0,
        )

        queue = float(
            downstream.get(
                "queue",
                0,
            )
        )

        occupancy = float(
            downstream.get(
                "occupancy",
                float(
                    downstream.get(
                        "vehicles",
                        0,
                    )
                )
                / capacity,
            )
        )

        queue_limit = (
            capacity
            * self.queue_threshold
        )

        return (
            queue <= queue_limit
            and occupancy <= self.occupancy_threshold
        )

    def evaluate(
        self,
        emergency_junction,
        traffic,
    ):
        self.emergency_junction = (
            emergency_junction
        )

        if not traffic:
            self.active = False
            self.blocked_junctions = []

            return GreenCorridorDecision(
                active=False,
                emergency_junction=emergency_junction,
                route=self.route,
                blocked_junctions=[],
                reason="No traffic state available.",
                priority="HIGH",
            )

        if emergency_junction not in self.route:
            self.route = (
                [emergency_junction]
                + self.route
            )

        try:
            start_index = self.route.index(
                emergency_junction
            )
        except ValueError:
            start_index = 0

        corridor_targets = (
            self.route[start_index:]
        )

        blocked = []

        for junction in corridor_targets:

            if junction not in traffic:
                blocked.append(junction)
                continue

            if not self._clearance_ok(
                traffic[junction]
            ):
                blocked.append(junction)

        self.blocked_junctions = blocked

        if blocked:
            self.active = False

            return GreenCorridorDecision(
                active=False,
                emergency_junction=emergency_junction,
                route=corridor_targets,
                blocked_junctions=blocked,
                reason=(
                    "Green corridor delayed because "
                    "downstream traffic clearance "
                    "is insufficient."
                ),
                priority="HIGH",
            )

        self.active = True

        return GreenCorridorDecision(
            active=True,
            emergency_junction=emergency_junction,
            route=corridor_targets,
            blocked_junctions=[],
            reason=(
                "Emergency Green Corridor ACTIVE."
            ),
            priority="HIGH",
        )

    def activate(
        self,
        emergency_junction=None,
        route=None,
    ):
        if emergency_junction is not None:
            self.emergency_junction = (
                emergency_junction
            )

        if route:
            self.route = list(route)

        self.active = True
        self.blocked_junctions = []

        return GreenCorridorDecision(
            active=True,
            emergency_junction=(
                self.emergency_junction
            ),
            route=self.route,
            blocked_junctions=[],
            reason=(
                "Emergency Green Corridor ACTIVE."
            ),
            priority="HIGH",
        )

    def deactivate(self):
        self.active = False
        self.emergency_junction = None
        self.blocked_junctions = []

        return GreenCorridorDecision(
            active=False,
            emergency_junction="",
            route=[],
            blocked_junctions=[],
            reason=(
                "Emergency Green Corridor CLEARED."
            ),
            priority="NORMAL",
        )

    def clear(self):
        """
        Compatibility method used by run_sumo.py.

        Clears the active emergency green corridor
        and resets its state.
        """
        return self.deactivate()

    def status(self):
        if self.active:
            corridor_status = "ACTIVE"
        elif self.blocked_junctions:
            corridor_status = "BLOCKED"
        else:
            corridor_status = "CLEARED"

        return {
            "active": self.active,
            "corridor_status": corridor_status,
            "emergency_junction": (
                self.emergency_junction
            ),
            "route": self.route,
            "blocked_junctions": (
                self.blocked_junctions
            ),
        }


GreenCorridor = GreenCorridorController