import time, requests

from datetime import datetime

url = 'https://discord.com/api/webhooks/xxxxxx'

class Message():

    def __init__(self, _msg):

        now = time.time()
        dt = datetime.fromtimestamp(now)
        message = {"content": f"[{str(dt)}] {str(_msg)}"}
        requests.post(url, data=message)
        print(message)
