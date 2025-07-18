import json
import time
import requests

used_tokens = set()


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
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"'
}


def get_new_tokens():
    response = requests.get("http://127.0.0.1:5000/custom.client.blobgame.io/tokens")
    return [token for token in json.loads(response.text) if token not in used_tokens]
successes, fails = 0, 0
while True:
    tokens = get_new_tokens()
    for token in tokens:
        data = {"captcha": token}
        response = requests.post(url, headers=headers, json=data)
        try:
            print(response.json()["token"])
            with open("jwts.txt", "a") as f:
                f.write(response.json()["token"] + "\n")
            successes += 1
            
        except:
            print("Error for", token)
            print(response.text)
            fails += 1
        used_tokens.add(token)
        print("Tried", len(used_tokens), "tokens")
        print("Successes:", successes)
        print("Fails:", fails)


    time.sleep(1)

