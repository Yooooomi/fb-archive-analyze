import sys
import json
import glob
from os import path
import emoji
import math
import plugins

class Message():
    def __init__(self, msg):
        self.sender = msg["sender_name"]
        self.ts = msg["timestamp_ms"]
        self.content = None
        if "content" in msg:
            self.content = msg["content"].encode("latin1").decode("UTF-8")

class Stat:
    def __init__(self, name):
        self.plugins = []
        self.name = name.encode("latin1").decode("UTF-8")

    def add_plugin(self, plugin):
        self.plugins.append(plugin)

    def add_message(self, msg):
        for p in self.plugins:
            p.on_add_message(msg)
        if msg.content != None:
            emojis = [x for x in msg.content if x in emoji.UNICODE_EMOJI]
            for em in emojis:
                for p in self.plugins:
                    p.on_add_emoji(em)

    def set_first_last(self, first, last):
        for p in self.plugins:
            p.on_set_first_last(first, last)

    def sumup(self):
        print()
        print(self.name)
        for p in self.plugins:
            print(p.sumup())
        print()

plugins = [
    plugins.LongestConv,
    plugins.TotalMessages,
    plugins.TotalCharacters,
    plugins.CharsPerMessages,
    plugins.MessagesPerDay,
    plugins.TotalEmojis,
    plugins.ConversationStarts,
    plugins.MostUsedEmojis,
    plugins.MostUsedWord,
    plugins.EmojisPerMessage,
]

def compute(messages):
    stats = {}
    first = Message(messages[0])
    last = Message(messages[len(messages) - 1])
    for msg in messages:
        msg = Message(msg)
        if msg.sender not in stats:
            st = Stat(msg.sender)
            stats[msg.sender] = st
            for p in plugins:
                st.add_plugin(p())
            st.set_first_last(first, last)
        stat = stats[msg.sender]
        stat.add_message(msg)
    for value in stats.values():
        value.sumup()

def main(args):
    files = []
    for directory in args:
        files.extend(glob.glob(path.join(directory, "message_*.json")))
    messages = []
    participants = []
    for file in files:
        with open(file, "r") as f:
            data = json.load(f)
            messages.extend(data["messages"])
    messages.sort(key=lambda x : x["timestamp_ms"])
    compute(messages)

if __name__ == "__main__":
    main(sys.argv[1:])