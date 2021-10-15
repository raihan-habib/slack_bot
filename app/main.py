from helper import *
from slack_conversation_history import *
from cprofiler_decorator import profile

logger = logger_init( __name__)

@profile(sort_by='cumulative', lines_to_print=10, strip_dirs=True)
def export_csv_slack_conversation_history():
    try:
        conversation_history = fetch_slack_conversation_history_list()
        conversation_history = format_history_data(conversation_history)
        df = create_dataframe(conversation_history)
        save_to_csv(df)
    except Exception as e:
        logger.error("Error occurred: {}".format(e))

if __name__ == "__main__":
    export_csv_slack_conversation_history()
