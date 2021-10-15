import logging
import logging.config
import os
import time
import yaml
import datetime as DT
from functools import lru_cache
from pydantic import BaseSettings

def logger_init(filename=__name__):
    # Load logger config
    with open('logger.yaml', 'r') as f:
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    
    return logging.getLogger(filename)

logger = logger_init( __name__)


def get_oldest_timestamp(last_day_num: int):
    today = DT.date.today()
    old_date = today - DT.timedelta(days=last_day_num)
    timestamp = time.mktime(old_date.timetuple())
    logger.info("Oldest timestamp: {}".format(timestamp))
    return timestamp

class Settings(BaseSettings):
    token: str = os.getenv("SLACK_BOT_TOKEN", "dev")
    channel_ids: list = os.getenv("CHANNEL_IDS", ["C029JE55LM9", "C02A7TG9RMW"])
    limit: int = int(os.getenv("LIMIT", 100))
    oldest: int = get_oldest_timestamp(int(os.getenv("OLDEST_DAY_NUM", 1)))
    conversation_history_file_name = 'output/conversation_history.csv'


@lru_cache()
def get_settings() -> BaseSettings:
    logger.info("Loading config settings from the environment...")
    return Settings()
