import time, requests

from datetime import datetime

url = 'https://discord.com/api/webhooks/1375453664885473341/l9ASZS3clm_RTXMvq7kT2D3_wMC3J3uMeUwbQB0w54uBqu8zIxpYLvYCdoL2iibfvi6n'

class Message():

    def __init__(self, _msg):

        now = time.time()
        dt = datetime.fromtimestamp(now)
        message = {"content": f"[{str(dt)}] {str(_msg)}"}
        requests.post(url, data=message)
        print(message)
