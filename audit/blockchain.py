"""
Q-TRAFFIC Blockchain-Style Audit Log

Lightweight SHA-256 hash-chain audit system.

This is NOT a decentralized blockchain network.
It is a tamper-evident local audit chain for
traffic-control decisions.
"""

import hashlib
import json
from datetime import datetime


class AuditBlockchain:

    def __init__(self):
        self.chain = []

    def calculate_hash(self, block):
        """Generate SHA-256 hash for a block."""

        block_string = json.dumps(
            block,
            sort_keys=True
        ).encode()

        return hashlib.sha256(
            block_string
        ).hexdigest()

    def add_decision(
        self,
        decision_type,
        scenario,
        route=None,
        signal_plan=None,
        metrics=None
    ):
        """Add a traffic-control decision to the audit chain."""

        previous_hash = (
            self.chain[-1]["hash"]
            if self.chain
            else "GENESIS"
        )

        block = {
            "index": len(self.chain),
            "timestamp": datetime.now().isoformat(),
            "decision_type": decision_type,
            "scenario": scenario,
            "route": route,
            "signal_plan": signal_plan,
            "metrics": metrics,
            "previous_hash": previous_hash
        }

        block["hash"] = self.calculate_hash(
            block
        )

        self.chain.append(block)

        return block

    def verify_chain(self):
        """Verify that the audit chain has not been modified."""

        for index, block in enumerate(self.chain):

            stored_hash = block["hash"]

            block_copy = block.copy()

            del block_copy["hash"]

            calculated_hash = self.calculate_hash(
                block_copy
            )

            if stored_hash != calculated_hash:
                return False

            if index == 0:

                if block["previous_hash"] != "GENESIS":
                    return False

            else:

                previous_block = self.chain[
                    index - 1
                ]

                if (
                    block["previous_hash"]
                    != previous_block["hash"]
                ):
                    return False

        return True

    def get_chain(self):
        """Return the complete audit history."""

        return self.chain


if __name__ == "__main__":

    audit = AuditBlockchain()

    audit.add_decision(
        decision_type="GREEN_CORRIDOR",
        scenario="Ambulance Emergency",
        route=[
            "J1",
            "J2",
            "J3",
            "J4"
        ],
        signal_plan={
            "J1": "50s GREEN",
            "J2": "50s GREEN",
            "J3": "50s GREEN",
            "J4": "50s GREEN"
        },
        metrics={
            "waiting_time": 18.0,
            "throughput": 155
        }
    )

    audit.add_decision(
        decision_type="SIGNAL_OPTIMIZATION",
        scenario="Ambulance Emergency",
        route=[
            "J1",
            "J2",
            "J3",
            "J4"
        ],
        signal_plan={
            "J1": "50s GREEN",
            "J2": "50s GREEN",
            "J3": "50s GREEN",
            "J4": "50s GREEN"
        }
    )

    print("\n" + "=" * 60)
    print("Q-TRAFFIC AUDIT BLOCKCHAIN")
    print("=" * 60)

    for block in audit.get_chain():

        print("\nBLOCK", block["index"])
        print("-" * 40)

        print("Decision :", block["decision_type"])
        print("Scenario :", block["scenario"])
        print("Route    :", block["route"])
        print("Previous :", block["previous_hash"])
        print("Hash     :", block["hash"])

    print("\nCHAIN VERIFICATION")
    print("-" * 40)

    print(
        "Valid :",
        audit.verify_chain()
    )