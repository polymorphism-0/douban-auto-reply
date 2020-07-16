import requests
import random
import time
import json

get_url = "http://127.0.0.1:8000/"
delete_url = "http://127.0.0.1:8000/delete?ip={ip}&port={port}"
http = "http://{ip}:{port}"


class Proxy:
    def __init__(self, logger):
        self.logger = logger
        self.proxy = {}
        self.update_proxy()

    def update_proxy(self):
        random_sleep = random.randint(4, 6)
        self.logger.info("Sleep for " + str(random_sleep) + " seconds")
        time.sleep(random_sleep)

        # Get a new proxy from the IP Proxy Pool
        r = requests.get(get_url, timeout=5)
        ip_ports = json.loads(r.text)
        if not ip_ports:
            return
        ip = ip_ports[0][0]
        port = ip_ports[0][1]
        self.proxy["http"] = http.format(ip=ip, port=port)
        self.logger.info("New proxy, " + str(self.proxy))

        # Delete the proxy from the IP Proxy Pool
        requests.get(delete_url.format(ip=ip, port=port), timeout=5)
