from slack_sdk.web import client
from config import get_settings
from helper import *

# Import WebClient from Python SDK (github.com/slackapi/python-slack-sdk)
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

settings = get_settings()
logger = logger_init( __name__)

client = WebClient(token=settings.token)

def fetch_slack_conversation_history_list():
    conversation_history = []
    for channel_id in settings.channel_ids:
        conversation_history.extend(get_by_channel_id(channel_id=channel_id))
    
    return conversation_history

def get_by_channel_id(channel_id=None):
    """
    Call the conversations.history method using the WebClient
    conversations.history returns the first 100 messages by default
    These results are paginated, see: https://api.slack.com/methods/conversations.history$pagination
    """
    conversation_history = []
    next_cursor = None

    try:
        while True:
            result = client.conversations_history(channel=channel_id, limit=settings.limit, oldest=settings.oldest, cursor=next_cursor)
            conversation_history.extend([msg for msg in result["messages"]])
            
            if result['has_more'] is False:
                break

            next_cursor = result['response_metadata']['next_cursor']
        
        logger.info("{} messages found in Channel_id: {}".format(len(conversation_history), channel_id))

    except SlackApiError as e:
        logger.error("Error in Channel_id: {} during fetch conversation history".format(channel_id))
        logger.error("{}".format(e))
        raise Exception({'ok': False, 'error': 'invalid_auth'})
    
    return conversation_history

def format_history_data(conversation_history):
    try:
        for index, item in enumerate(conversation_history):
            conversation_history[index]['text'] = create_dict_from(item['text'])
    except TypeError as e:
        logger.error(e)
    
    return conversation_history