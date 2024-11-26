import sys
import requests
import threading
import dns.resolver
from time import sleep

# banner
def banner():
    print('''
    
 ██████╗ ███████╗ ██████╗ █████╗ ██████╗    ██╗  ██╗ ██████╗ ██╗  ██╗
██╔═══██╗██╔════╝██╔════╝██╔══██╗██╔══██╗   ██║  ██║██╔═████╗██║  ██║
██║   ██║███████╗██║     ███████║██████╔╝   ███████║██║██╔██║███████║
██║   ██║╚════██║██║     ██╔══██║██╔══██╗   ╚════██║████╔╝██║╚════██║
╚██████╔╝███████║╚██████╗██║  ██║██║  ██║███████╗██║╚██████╔╝     ██║
 ╚═════╝ ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝ ╚═════╝      ╚═╝
                                                        ''')

# Function to check CNAME records for a subdomain
def check_cname(subdomain, domain, output_file):
    full_domain = f"{subdomain}.{domain}"  # Construct the full domain name
    cname_record = None  # Initialize CNAME record

    try:
        # Attempt to resolve the CNAME record
        answers = dns.resolver.resolve(full_domain, "CNAME")
        cname_record = answers[0].to_text()  # Extract the CNAME record
    except dns.resolver.NoAnswer:
        pass  # No CNAME record exists
    except dns.resolver.NXDOMAIN:
        pass  # Subdomain does not exist
    except dns.exception.Timeout:
        pass  # DNS query timed out

    # Save the results with the required format
    with open(output_file, "a") as file:
        file.write(f"{full_domain}\n")  # Write the subdomain
        if cname_record:
            file.write(f"{cname_record}\n")  # Write the CNAME if it exists

# Function to check if a subdomain is reachable and perform DNS enumeration
def check_subdomain(subdomain, domain, output_file, progress):
    full_domain = f"{subdomain}.{domain}"  # Construct the full subdomain name
    url = f"http://{full_domain}"  # Construct the full subdomain URL

    try:
        # Check if the subdomain is reachable
        response = requests.get(url, timeout=5)
    except (requests.ConnectionError, requests.Timeout):
        pass  # Ignore connection and timeout errors
    else:
        # If reachable, perform DNS enumeration
        check_cname(subdomain, domain, output_file)

    # Update the progress
    with progress["lock"]:
        progress["completed"] += 1
        percentage = (progress["completed"] / progress["total"]) * 100
        print(f"\rProgress: {percentage:.2f}% ({progress['completed']}/{progress['total']})", end="", flush=True)

# Function to manage threads
def run_threads(subdomains, domain, output_file):
    threads = []
    progress = {"completed": 0, "total": len(subdomains), "lock": threading.Lock()}
    for subdomain in subdomains:
        thread = threading.Thread(target=check_subdomain, args=(subdomain, domain, output_file, progress))
        threads.append(thread)
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    # Ensure the script is executed correctly
    if len(sys.argv) != 2:
        print("Usage: python3 subdomain_enumeration.py <domain>")
        sys.exit(1)

    banner()
    # Read the domain and subdomains file
    domain = sys.argv[1]
    output_file = "results.txt"  # Output file for discovered subdomains and CNAMEs

    try:
        with open("subdomains.txt", "r") as file:
            subdomains = file.read().splitlines()  # Read and split subdomains
    except FileNotFoundError:
        print("Error: subdomains.txt file not found.")
        sys.exit(1)

    # Clear the output file before starting
    with open(output_file, "w") as file:
        pass  # Create an empty file or clear its contents

    # Run the subdomain enumeration
    run_threads(subdomains, domain, output_file)
    print("Subdomain enumeration Finished!")
    print("\nStarting subdomain takeover scan....")
