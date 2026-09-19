from pathlib import Path
import os
import shutil
import subprocess


def find_netconvert():
    # 1. Try PATH first
    for name in ("netconvert", "netconvert.exe"):
        found = shutil.which(name)
        if found:
            return found

    # 2. Try SUMO_HOME
    sumo_home = os.environ.get("SUMO_HOME")

    if sumo_home:
        candidate = Path(sumo_home) / "bin" / "netconvert.exe"
        if candidate.exists():
            return str(candidate)

    # 3. Common Windows SUMO installation
    common_path = Path(
        r"C:\Program Files (x86)\Eclipse\Sumo\bin\netconvert.exe"
    )

    if common_path.exists():
        return str(common_path)

    return None


def build():
    net = find_netconvert()

    base = Path(__file__).resolve().parent

    if not net:
        print("ERROR: SUMO netconvert could not be found.")
        return False

    print(f"Using netconvert: {net}")

    cmd = [
        net,
        "-n",
        str(base / "nodes.nod.xml"),
        "-e",
        str(base / "edges.edg.xml"),
        "--junctions.join=false",
        "-o",
        str(base / "network.net.xml"),
    ]

    print("Generating SUMO network...")

    subprocess.run(cmd, check=True)

    print(f"Network created successfully:")
    print(base / "network.net.xml")

    return True


if __name__ == "__main__":
    build()