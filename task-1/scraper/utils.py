import random
import time
from config.settings import USER_AGENTS, DELAY

def get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS)
    }

def sleep():
    time.sleep(DELAY)