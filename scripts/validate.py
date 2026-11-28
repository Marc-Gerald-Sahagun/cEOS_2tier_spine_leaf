#!/usr/bin/env python3

import subprocess

def cli(node, command): 
    result = subprocess.run(["docker", "exec", node, "Cli", "-p", "15", "-c", command],
                            capture_output=True, text=True,)
    return result.stdout

def report(name, ok):
    print(f"{'PASS' if ok else 'FAIL'} {name}") # PASS if true else FAIL
    return ok

def check_bgp(nodes, expected):
    # Check that each BGP node has the expected number of Established neighbors
    results = []
    for node in nodes: 
        out = cli(node, "show ip bgp summary")
        up = 0
        for line in out.splitlines():
            if "Estab" in line:
                up = up + 1
        results.append(report(f"{node} BGP {up}/{expected}", up == expected))
    return results

def check_mlag(nodes):
    # Check that each MLAG leaf is active and its peer config is consistent
    results = []
    for node in nodes:
        out = cli(node, "show mlag")
        active = "Active" in out and "Connected" in out
        consistent = "consistent" in out and "inconsistent" not in out
        results.append(report(f"{node} MLAG active and consistent", active and consistent))
    return results

def check_server_address(servers):
    # Displays bond0 IP addresses of the servers
    for server in servers:
        out = subprocess.run(["docker", "exec", server, "ip", "addr", "show"],
                             capture_output=True, text=True,)
        for line in out.stdout.splitlines():
            line = line.strip()
            if line.startswith("inet "):
                if "brd" in line or "host" in line:
                    continue
                print(f" {server}: ", line)

def main():
    results = []
    results += check_bgp(["spine1", "spine2"], 6)
    results += check_bgp(["leaf1", "leaf2", "leaf3", "leaf4", "leaf5", "leaf6"], 2)
    results += check_mlag(["leaf1", "leaf2", "leaf3", "leaf4"])
    sum = 0
    for result in results:
        if result == True:
            sum = sum + 1
        
    print(f"{sum}/{len(results)} checks passed")
    check_server_address(["server1", "server2", "server3", "server4"])

if __name__ == "__main__":
    main()

