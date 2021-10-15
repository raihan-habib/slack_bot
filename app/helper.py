import re
import pandas as pd
from pandas.core.frame import DataFrame
from config import get_settings
from config import logger_init

settings = get_settings()
logger = logger_init( __name__)


def flatten_nested_json_df(df: DataFrame):

    df = df.reset_index()

    logger.debug(f"original shape: {df.shape}")
    logger.debug(f"original columns: {df.columns}")


    # search for columns to explode/flatten
    s = (df.applymap(type) == list).all()
    list_columns = s[s].index.tolist()

    s = (df.applymap(type) == dict).all()
    dict_columns = s[s].index.tolist()

    logger.debug(f"lists: {list_columns}, dicts: {dict_columns}")
    while len(list_columns) > 0 or len(dict_columns) > 0:
        new_columns = []

        for col in dict_columns:
            logger.debug(f"flattening: {col}")
            # explode dictionaries horizontally, adding new columns
            horiz_exploded = pd.json_normalize(df[col]).add_prefix(f'{col}.')
            horiz_exploded.index = df.index
            df = pd.concat([df, horiz_exploded], axis=1).drop(columns=[col])
            new_columns.extend(horiz_exploded.columns) # inplace

        for col in list_columns:
            logger.debug(f"exploding: {col}")
            # explode lists vertically, adding new columns
            df = df.drop(columns=[col]).join(df[col].explode().to_frame())
            new_columns.append(col)

        # check if there are still dict o list fields to flatten
        s = (df[new_columns].applymap(type) == list).all()
        list_columns = s[s].index.tolist()

        s = (df[new_columns].applymap(type) == dict).all()
        dict_columns = s[s].index.tolist()

        logger.debug(f"lists: {list_columns}, dicts: {dict_columns}")

    logger.debug(f"final shape: {df.shape}")
    logger.debug(f"final columns: {df.columns}")
    return df

def handle_exceptional_key(key: str):
    return "Execution condition" if (key == "redcircle" or key == "green") else key

def remove_special_characters_from(key: str):
    return re.sub(r'[^a-zA-Z]', '', key)

def create_dict_from(msg: str):
    msg_dict = {}
    msg_list = msg.split('\n')
    for item in msg_list:
        item = item.strip(' *:')
        try:
            if item != '':
                (key, value) = item.split(": ")
                key = remove_special_characters_from(key)
                key = handle_exceptional_key(key)
                msg_dict[key] = value.strip()

        except ValueError as e:
            logger.error(item)
            logger.error(e)

    return msg_dict

def create_dataframe(conversation_history: list):
    df = pd.DataFrame(conversation_history)
    return flatten_nested_json_df(df)

def save_to_csv(df: DataFrame):
    df.to_csv(settings.conversation_history_file_name, index=False)

