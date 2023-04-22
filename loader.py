import json
import os
import pandas as pd
from datetime import datetime
from pathlib import Path


CHATDF_FILENAME = "chat_df.csv"
MSGDF_FILENAME = "msg_df.csv"
JSON_FILENAME = "message_"

# Facebook JSON badly encoded
# https://stackoverflow.com/a/62160255/15411117
def parse_obj(obj):
    if isinstance(obj, str):
        return obj.encode('latin_1').decode('utf-8')

    if isinstance(obj, list):
        return [parse_obj(o) for o in obj]

    if isinstance(obj, dict):
        return {key: parse_obj(item) for key, item in obj.items()}

    return obj

def parse_from_json(path=None):
    """
    Parses JSON data into two pandas DataFrames:
    One to hold the data for each chat and one to hold all messages.
    Pass in the path where your chat data was extracted or leave empty
    to use current directory

    Typical usage would have path = {facebook_data_dir}/messages/inbox

    Parameters
    ----------
    path: str
        Path of extracted facebook messages, typically looks like:
        `/path/to/facebook_data_dir/messages/inbox` or
        `/path/to/facebook_data_dir/messages/archived_threads` or
        `/path/to/facebook_data_dir/messages/message_requests`

    Returns
    -------
    pandas.DataFrame, pandas.DataFrame
        returns chat_df and msg_df, DataFrames containing information on
        chats and messages, respectively
    """
    path = path or os.getcwd()
    path = Path(path)
    if not os.path.isdir(path):
        raise NotADirectoryError(f"{path} is not a directory")
    messages_dir = [path / mdir for mdir in os.listdir(path)]
    all_files = [msg_dir / json_file for msg_dir in messages_dir for json_file in os.listdir(msg_dir) if json_file.startswith(JSON_FILENAME)]

    chat_data = []
    threads = set()
    chat_cols = ['participants', 'title',
                 'is_still_participant', 'thread_type', 'thread_path']
    message_data = []
    msg_cols = ['thread_path', 'timestamp', 'msg',
                'sender', 'sticker', 'photos', 'videos', 'call_duration', 'audio', 'audio_duration']

    for json_file in all_files:
        # open file as latin1 an encode to utf-8
        with open(json_file) as json_file:
            current_chat = parse_obj(json.load(json_file))

        thread_path = current_chat['thread_path']

        participants = [x['name']
                        for x in current_chat.get('participants', '')]
        title = current_chat.get('title', '')
        is_still_participant = current_chat.get('is_still_participant', '')
        thread_type = current_chat.get('thread_type', '')

        # avoid duplicate chat entries for chats with multiple message_x.json files
        if thread_path not in threads:
            threads.add(thread_path)
            chat_data.append(
                [participants, title, is_still_participant, thread_type, thread_path])

        for msg in current_chat['messages']:
            ts = msg.get('timestamp_ms', 0) // 1000
            body = msg.get('content', None)
            sender = msg.get('sender_name', None)
            sticker = msg.get('sticker', None)
            photos = msg.get('photos', None)
            videos = msg.get('videos', None)
            audio = msg.get('audio_files', None)
            audio = audio[0]['uri'] if audio else None
            call_duration = msg.get('call_duration', None)
            audio_duration = None



            # if audio:
            #     # print(f"Found audio file: {audio[0]['uri']}")
            #     # audio_duration = ffprobe_duration(audio[0]['uri'])
            #     try:
            #         # relative_path = Path(audio[0]['uri'])
            #         # audio = relative_path.resolve()
            #         audio_duration = ffprobe_duration(audio[0]['uri'])
            #         # to minutes - round to 1 decimal places
            #         audio_duration = round(audio_duration / 60, 1)
            #     except FileNotFoundError:
            #         audio_duration = None

            message_data.append(
                [thread_path, ts, body, sender, sticker, photos, videos, call_duration, audio, audio_duration])

    chat_df = pd.DataFrame(chat_data, columns=chat_cols)
    chat_df.set_index('thread_path', inplace=True)
    msg_df = pd.DataFrame(message_data, columns=msg_cols)
    msg_df['timestamp'] = msg_df['timestamp'].apply(datetime.fromtimestamp)

    return chat_df, msg_df


def load_from_csv(path=None):
    """ reads and returns DataFrame from persisted DataFrames in CSV format.
        Pass in a path to where the CSV files are located or leave blank to use current directory """
    chat_file = check_path(path, CHATDF_FILENAME)[0]
    msg_file = check_path(path, MSGDF_FILENAME)[0]

    chat_df = pd.read_csv(chat_file, converters={
                          "participants": eval}, index_col='thread_path')
    msg_df = pd.read_csv(msg_file, index_col=0)
    # msg_df['timestamp'] = pd.to_datetime(msg_df['timestamp'])

    return chat_df, msg_df


def persist(chat_df, msg_df):
    chat_df.to_csv(CHATDF_FILENAME)
    msg_df.to_csv(MSGDF_FILENAME)

    return True


def check_path(path, fmt):
    if path and not os.path.isdir(path):
        print("%s is not a valid directory" % path)
        raise NotADirectoryError

    filenames = os.listdir(path) if path else os.listdir()
    abs_path = os.path.abspath(path) if path else os.getcwd()
    files = [os.path.join(abs_path, f) for f in filenames if f.endswith(fmt)]
    matching_files = [f for f in files if f.endswith(fmt)]

    if len(matching_files) == 0:
        print("No %s file found at %s" % (fmt, abs_path))
        raise FileNotFoundError

    return matching_files

def ffprobe_duration(filename):
    import subprocess
    cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', filename]
    return float(subprocess.check_output(cmd))


if __name__ == "__main__":
    chat_df, msg_df = parse_from_json()
    print(chat_df)
    print(msg_df)
