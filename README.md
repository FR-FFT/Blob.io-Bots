## Videos
(In all of the videos, I am playing as neuro and the other neuro is a bot controlled by me.)


https://github.com/user-attachments/assets/b19f60c8-841e-4f05-ba1f-dc814a3d61cc



https://github.com/user-attachments/assets/77d22d3b-885d-41da-94a2-7ff1cdba61dd




https://github.com/user-attachments/assets/bd0f4ee4-aef1-44c9-877b-ed95ab0582f8


## To run
* Download all of the files. The first thing to do is to obtain the JWTs needed for authentication. There are two ways to do this:
### Manually
* Open an incognito browser window. Go to blobgame.io, open the developer tools (ctrl + shift + i), and switch to the network tab.
<img width="570" height="37" alt="image" src="https://github.com/user-attachments/assets/055b5136-016c-441e-bfe0-46fd61d593e4" />

* Change the filter to socket.
<img width="587" height="28" alt="image" src="https://github.com/user-attachments/assets/6ee7e773-e3ab-4654-81fd-9e2769fde73f" />

* Enter a game. Ignore any warnings about it being insecure - this is because blob.io uses http instead of https.
There will be a websocket connection in the dev tools.
<img width="670" height="177" alt="image" src="https://github.com/user-attachments/assets/6a465d32-e6c9-4c14-a199-3c9b5f95689a" />

* Copy all of the long text in Sec-Websocket-Protocol after 7, 3, WaWdft, (you can test on jwt.io whether you have done it correctly - it should be a valid jwt).
<img width="667" height="690" alt="image" src="https://github.com/user-attachments/assets/9c46ccfe-6f6a-47ac-a6c9-4a13be570c48" />

* Paste this into jwts.txt, removing what was there before (because they won't work for more than a few days).
* You will probably want at least two of these, so repeat the process.

### Semi-automatically
* *Install [captcha-harvester](https://github.com/NoahCardoza/CaptchaHarvester). It will not run on the latest python versions, so use either `python3.9 -m pip install captcha-harvester`, or `uv python pin 3.9` and `uvx harvester --from captcha-harvester`
* *Run `harvester -k 6LefTNUUAAAAAKgrowGdOhrnKxcm2ql40YRck04V -d custom.client.blobgame.io recaptcha-v2` and run get_jwts.py at the same time (the captcha tokens seem to be time-limited, they will invalidate if not used withina few minutes).

## Running the bots
* First run server.py. Modify `TARGET_SERVER_IP_PORT = "51.195.60.134:6001"` to change the server. Modify `"name": f"neuro",` to change the bot names.
* Install script.js using a userscript extension like tampermonkey, violetmonkey, etc.
* Make sure you connect to the same server.
* Use 'a' to split the bots and 's' to feed, and 'o' to toggle the bots going to your mouse.
