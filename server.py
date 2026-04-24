import asyncio
import json
import os
import subprocess
import time
import requests
from server import run_bots


def check_existing_jwts():
    if not os.path.exists("jwts.txt"):
        return []
    with open("jwts.txt", "r") as f:
        return [line.strip() for line in f.readlines() if line.strip()]


def harvest_captchas(needed_count, wipe_existing=False):
    if wipe_existing:
        with open("jwts.txt", "w") as f:
            pass  # clear the file

    print(f"Starting captcha harvester. We need {needed_count} JWTs.")
    harvester_cmd = [
        "uv",
        "run",
        "harvester",
        "--browser",
        r"C:\Users\Foo\scoop\apps\googlechrome\147.0.7727.102\chrome.exe",
        "--site-key",
        "6LfYPLosAAAAAJp4dj_N92aT6CFkzeCgWVuCy6QC",
        "--domain",
        "custom.client.blobgame.io",
        "--data-action",
        "login",
        "recaptcha-v3",
    ]

    # Start the harvester process
    harvester_proc = subprocess.Popen(harvester_cmd)

    # Wait a bit for the harvester server to spin up
    time.sleep(3)

    print(
        "Harvester started. Please open http://127.0.0.1:5000 in your browser to solve captchas."
    )

    url = "https://api.blobgame.io:988/api/users/checkcaptcha"
    headers = {
        "Accept": "*/*",
        "Accept-Language": "en-GB,en;q=0.9",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "application/json;charset=utf-8",
        "Origin": "http://custom.client.blobgame.io",
        "Pragma": "no-cache",
        "Referer": "http://custom.client.blobgame.io/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
    }

    used_tokens = set()
    successes = 0

    try:
        while successes < needed_count:
            try:
                res = requests.get(
                    "http://127.0.0.1:5000/custom.client.blobgame.io/tokens",
                    timeout=2.0,
                )
                if res.status_code == 200:
                    tokens = [t for t in res.json() if t not in used_tokens]
                    for token in tokens:
                        if successes >= needed_count:
                            break

                        used_tokens.add(token)
                        data = {"captcha": token, "pl": 3, "ver": 2}

                        try:
                            # Serialize explicitly to match JS fetch exactly
                            json_payload = json.dumps(data, separators=(",", ":"))
                            api_res = requests.post(
                                url, headers=headers, data=json_payload, verify=False
                            )
                            if api_res.status_code == 200:
                                jwt_token = api_res.json().get("token")
                                if jwt_token:
                                    print("Successfully retrieved a JWT token!")
                                    with open("jwts.txt", "a") as f:
                                        f.write(jwt_token + "\n")
                                    successes += 1
                                else:
                                    print(
                                        "API response didn't contain a token:",
                                        api_res.text,
                                    )
                            else:
                                print(
                                    f"API Error ({api_res.status_code}):",
                                    api_res.text,
                                )
                        except Exception as e:
                            print(f"Error making POST request: {e}")

                else:
                    print(f"Failed to fetch tokens from harvester ({res.status_code})")
            except requests.exceptions.RequestException:
                pass  # Ignore connection errors if harvester isn't fully ready or returning tokens

            if successes < needed_count:
                print(f"Waiting for captchas... ({successes}/{needed_count})")
                time.sleep(2)
    except KeyboardInterrupt:
        print("\nHarvesting interrupted by user.")
    finally:
        print("Terminating harvester process...")
        harvester_proc.terminate()
        harvester_proc.wait()


def main():
    print("Welcome to Blob.io Bot Farm!")

    server_ip = "51.195.60.134:6001"
    num_proxy_bots = 0
    num_non_proxy_bots = 1 
    proxies = []
    run_control_server = True

    total_bots = num_proxy_bots + num_non_proxy_bots
    existing_jwts = check_existing_jwts()

    print(f"Current configuration needs {total_bots} JWTs.")
    print(f"Found {len(existing_jwts)} existing JWTs in jwts.txt.")

    refresh = False

    while True:
        ans = input("Do you want to refresh jwts.txt? (y/n): ").strip().lower()
        if ans in ["y", "yes"]:
            refresh = True
            break
        elif ans in ["n", "no"]:
            refresh = False
            break

    if refresh:
        print("Refreshing JWTs...")
        harvest_captchas(total_bots, wipe_existing=True)
    elif len(existing_jwts) < total_bots:
        needed = total_bots - len(existing_jwts)
        print(f"Not enough existing JWTs. We still need {needed} more.")
        harvest_captchas(needed, wipe_existing=False)
    else:
        print("Using existing JWTs.")

    # Check one more time before starting
    final_jwts = check_existing_jwts()
    if len(final_jwts) < total_bots:
        print(
            "WARNING: Still don't have enough JWTs. Proceeding anyway, but some bots may not spawn."
        )

    print("Starting bots via main.py!")
    try:
        asyncio.run(
            run_bots(
                server_ip=server_ip,
                num_proxy_bots=num_proxy_bots,
                num_non_proxy_bots=num_non_proxy_bots,
                proxies=proxies,
                run_control_server=run_control_server,
            )
        )
    except KeyboardInterrupt:
        print("\nShutting down bot farm.")


if __name__ == "__main__":
    import urllib3

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    main()
