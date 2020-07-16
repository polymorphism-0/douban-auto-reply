import random
import time
import requests
from lxml import etree
import json

import re
import urllib.parse
import base64
import hmac
from hashlib import sha1

import config
from util.logmodule import LogModule
from util.proxy import Proxy

logger = LogModule()
proxy = Proxy(logger)

# 豆瓣的sig算法
def hash_hmac(key, code, sha1):
    hmac_code = hmac.new(key.encode(), code.encode(), sha1).digest()
    return base64.b64encode(hmac_code).decode()


def get_topic(session):
    # 找到首页最早发出的0回复的帖子，如果没有返回None
    try:
        r = session.get(config.group_topics_url, proxies=proxy.proxy, timeout=5)
        if r.status_code != 200:
            logger.error("Failed to retrieve group topics: " + str(r.status_code))
            proxy.update_proxy()
            return None
        group_json = json.loads(r.text)
        for topic in reversed(group_json["topics"]):
            if topic["comments_count"] == 0:
                topic_id = re.findall("\d+", topic["url"])[0]
                return topic_id
        return None
    except Exception as e:
        logger.error("Failed to send request: " + str(e))
        proxy.update_proxy()
        return None


def post_comment(session, topic_id):
    try:
        create_comment_url = config.comment_url_template.format(topic_id=topic_id)
        # 随机选择一条回复
        comment = random.choice(config.comment_list)
        timestamp = str(int(time.time()))
        sig = hash_hmac(
            config.client_secret,
            config.sig_code_template.format(topic_id=topic_id, timestamp=timestamp),
            sha1,
        )
        content = config.comment_content_template.format(
            comment=urllib.parse.quote(comment),
            sig=urllib.parse.quote(sig),
            timestamp=timestamp,
        )
        r = session.post(
            create_comment_url, data=content, proxies=proxy.proxy, timeout=5
        )
        logger.info(
            "comment: {}, {}, status_code: {}".format(
                comment, create_comment_url, r.status_code
            )
        )
        if r.status_code == 200 or r.status_code == 404:
            return True
        else:
            proxy.update_proxy()
            return False
    except Exception as e:
        logger.error("Failed to send request: " + str(e))
        proxy.update_proxy()
        return False


if __name__ == "__main__":
    refresh_count = 0
    reply_count = 0
    continuous_count = 0
    proxy_count = 0
    proxy_threshold = random.randint(50, 80)

    s = requests.Session()
    s.headers.update(config.headers)

    while True:
        refresh_count += 1
        logger.info("第" + str(refresh_count) + "次刷新小组首页")
        topic_id = get_topic(s)

        if topic_id and post_comment(s, topic_id):
            reply_count += 1
            logger.info("第" + str(reply_count) + "次回复")
            continuous_count += 1
            if continuous_count > 4:
                continuous_count = 0
        else:
            continuous_count = 0

        # 为了避免豆瓣反爬虫机制，连续回复的次数越多，sleep的时间越长
        random_sleep = random.randint(10, 20) + continuous_count * 4
        logger.info("Sleep for " + str(random_sleep) + " seconds")
        time.sleep(random_sleep)

        # 当前的proxy用到一定次数之后，换成一个新的
        proxy_count += 1
        if proxy_count == proxy_threshold:
            proxy.update_proxy()
            proxy_count = 0
            continuous_count = 0
            proxy_threshold = random.randint(50, 80)
