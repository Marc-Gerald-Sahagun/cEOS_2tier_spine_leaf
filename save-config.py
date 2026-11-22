#!/usr/bin/env python3
import subprocess
from pathlib import Path

nodes = ["leaf1", "leaf2", "leaf3", "leaf4", "leaf5", "leaf6", "spine1", "spine2"]
configs = Path(__file__).parent / "configs"

for node in nodes:
    result = subprocess.run(
        ["docker", "exec", node, "Cli", "-p", "15", "-c", "show running-config"],
        capture_output=True, text=True,
    )
    if result.returncode != 0 or not result.stdout.strip():
        print(f"FAILED {node}: {result.stderr.strip()}")
        continue

    # Drop the echoed command line and any blank lines at the top.
    lines = [l for l in result.stdout.splitlines() if not l.startswith("> show")]
    while lines and not lines[0].strip():
        lines.pop(0)
    text = "\n".join(lines) + "\n"

    # Refuse to save a switch that booted without its config.
    if f"hostname {node}" not in text or "No startup-config was found" in text:
        print(f"SKIPPED {node}: no hostname {node} line, or it is in Zero Touch mode")
        continue

    target = configs / f"{node}.cfg"
    if target.exists():
        (configs / f"{node}.cfg.bak").write_text(target.read_text())
    target.write_text(text)
    print(f"saved {node}")
