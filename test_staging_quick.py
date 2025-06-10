#!/usr/bin/env python3
"""
Quick diagnostic test for staging instance
"""

import requests
from colorama import init, Fore

init(autoreset=True)

STAGING_URL = "http://localhost:5002"

print(f"\n{Fore.CYAN}Quick Staging Diagnostics")
print("=" * 40)

# Test basic connectivity
endpoints = [
    ("/", "Homepage"),
    ("/clients", "Clients"),
    ("/crpa_dashboard", "CRPA Dashboard"),
    ("/clients/quick-add", "Quick Add Form"),
    ("/static/style.css", "CSS"),
]

working = []
broken = []

for endpoint, name in endpoints:
    try:
        resp = requests.get(f"{STAGING_URL}{endpoint}", timeout=2)
        if resp.status_code == 200:
            print(f"{Fore.GREEN}✓ {name:20} OK")
            working.append(name)
        else:
            print(f"{Fore.RED}✗ {name:20} {resp.status_code}")
            broken.append(f"{name} ({resp.status_code})")
    except Exception as e:
        print(f"{Fore.RED}✗ {name:20} ERROR: {str(e)[:30]}")
        broken.append(f"{name} (ERROR)")

print(f"\n{Fore.CYAN}Summary:")
print(f"{Fore.GREEN}Working: {len(working)}/{len(endpoints)}")
print(f"{Fore.RED}Broken: {len(broken)}/{len(endpoints)}")

if broken:
    print(f"\n{Fore.YELLOW}Issues found:")
    for issue in broken:
        print(f"  - {issue}")

print(f"\n{Fore.YELLOW}Note: Staging has database schema issues.")
print(f"The production deployment would need schema migrations.")