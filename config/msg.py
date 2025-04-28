import requests, time

from datetime import datetime

url = 'https://discord.com/api/webhooks/1349690403829448725/7snHkoLZftpXa58O1KVS1NzhUoN9hBm2QUIwxAMcTFIHkEESIO8uHS-yFk3QPuqNcpPq'

class Message():

    def __init__(self, _msg):

        now = time.time()
        dt = datetime.fromtimestamp(now)
        message = {"content": f"[{str(dt)}] {str(_msg)}"}
        requests.post(url, data=message)
        print(message)
