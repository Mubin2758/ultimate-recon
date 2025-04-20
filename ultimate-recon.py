#!/usr/bin/env python3

import os
import sys
import argparse
import subprocess
import shutil
from datetime import datetime

# Function to run a command and save its output to a file
def run_command(command, output_file):
    with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True) as process:
        with open(output_file, "w") as f:
            for line in process.stdout:
                f.write(line)

# Tool existence checker: exits if any required tool is missing
def check_dependencies(tools):
    for tool in tools:
        if shutil.which(tool) is None:
            print(f"❌ ERROR: '{tool}' is not installed or not in PATH.")
            sys.exit(1)

# Subfinder for passive subdomain enumeration
def subfinder_enum(domain, folder):
    print(f"[+] Running: subfinder -d {domain} -silent")
    run_command(["subfinder", "-d", domain, "-silent"], f"{folder}/subfinder.txt")

# Amass for more thorough subdomain enum
def amass_enum(domain, folder):
    print(f"[+] Running: amass enum -passive -d {domain}")
    run_command(["amass", "enum", "-passive", "-d", domain], f"{folder}/amass.txt")

# Merge all subdomains and sort/unique them
def merge_subdomains(folder):
    print("[+] Merging results...")
    with open(f"{folder}/all_subs.txt", "w") as outfile:
        subprocess.run(f"cat {folder}/*.txt | sort -u", shell=True, stdout=outfile, text=True)

# Probe alive hosts using httpx
def probe_httpx(folder):
    print("[+] Probing for alive domains with httpx...")
    run_command(["httpx", "-l", f"{folder}/all_subs.txt", "-silent"], f"{folder}/alive.txt")

# Use gau to get historical URLs
def run_gau(domain, folder):
    print("[+] Running gau...")
    run_command(["gau", domain], f"{folder}/gau.txt")

# Run ffuf for directory brute forcing
def run_ffuf(folder):
    print("[+] Running ffuf on alive domains...")
    alive_file = f"{folder}/alive.txt"
    with open(alive_file, "r") as f:
        urls = [line.strip() for line in f.readlines()]
    
    for i, url in enumerate(urls):
        ffuf_out = f"{folder}/ffuf_{i}.txt"
        run_command([
            "ffuf", "-u", f"{url}/FUZZ", "-w", "/usr/share/wordlists/dirb/common.txt", "-mc", "200"
        ], ffuf_out)

# Beautify output folder name with timestamp
def create_output_folder(domain):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    folder = f"{domain}_{timestamp}"
    os.makedirs(folder, exist_ok=True)
    return folder

# Argument parser
def parse_args():
    parser = argparse.ArgumentParser(description="🧠 ULTIMATE RECON TOOL 🧠")
    parser.add_argument("domain", help="Target domain (e.g. tesla.com)")
    parser.add_argument("--amass", action="store_true", help="Enable amass enumeration")
    parser.add_argument("--httpx", action="store_true", help="Probe alive domains with httpx")
    parser.add_argument("--gau", action="store_true", help="Fetch archived URLs with gau")
    parser.add_argument("--ffuf", action="store_true", help="Brute-force directories with ffuf")
    return parser.parse_args()

# Main execution logic
def main():
    args = parse_args()
    domain = args.domain
    folder = create_output_folder(domain)

    print(f"\n[~] Starting ULTIMATE RECON on {domain} 🚀\n")

    # Check if required tools are available
    required = ["subfinder"]
    if args.amass: required.append("amass")
    if args.httpx: required.append("httpx")
    if args.gau: required.append("gau")
    if args.ffuf: required.append("ffuf")
    check_dependencies(required)

    # Run selected modules
    subfinder_enum(domain, folder)
    if args.amass:
        amass_enum(domain, folder)
    merge_subdomains(folder)
    if args.httpx:
        probe_httpx(folder)
    if args.gau:
        run_gau(domain, folder)
    if args.ffuf:
        run_ffuf(folder)

    print(f"\n✅ Recon complete! Output saved in: {folder}\n")

if __name__ == "__main__":
    main()
