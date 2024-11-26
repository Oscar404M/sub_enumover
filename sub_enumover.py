import subprocess
import sys

if len(sys.argv) != 2:
        print("Usage: python3 subdomain_enumeration.py <domain>")
        sys.exit(1)

    # Read the domain and subdomains file
domain = sys.argv[1]
subprocess.run(["python", "./subdomain_enumeration.py", f"{domain}"], check=True)

subprocess.run([
    "python", "./takeover.py", 
    "-l", "./results.txt", 
    "-o", "taken.txt", 
    "-T", "20", 
    "-v"
], check=True)
