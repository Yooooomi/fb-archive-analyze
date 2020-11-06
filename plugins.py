import math
import re

class StatTrigger:
    def on_add_message(self, msg):
        pass

    def on_add_emoji(self, emoji):
        pass

    def on_set_first_last(self, first, last):
        pass

    def sumup(self):
        return "NOT SET"

class LongestConv(StatTrigger):
    def __init__(self):
        self.first = None
        self.last = None
        self.time_ts = 0
        self.tmp_first = None
        self.tmp_last = None
        self.tmp_time_ts = 0

    def on_set_first_last(self, first, last):
        self.first = first
        self.last = last

    def on_add_message(self, msg):
        ten_minutes = 1000 * 60 * 10
        if self.tmp_first == None:
            self.tmp_first = msg
        # Someone responded in more than 10 minutes
        if self.tmp_last != None and msg.ts > self.tmp_last.ts + ten_minutes:
            if self.tmp_last.ts - self.tmp_first.ts > self.time_ts:
                self.first = self.tmp_first
                self.last = self.tmp_last
                self.time_ts = self.last.ts - self.first.ts
            self.tmp_first = msg
        self.tmp_last = msg

    def sumup(self):
        minute = 1000 * 60
        return "{} minutes, started with {} and ended with {}".format(self.time_ts // minute, self.first.content, self.last.content)

class TotalMessages(StatTrigger):
    def __init__(self):
        self.nb = 0

    def on_add_message(self, msg):
        self.nb += 1

    def sumup(self):
        return "{} total message".format(self.nb)

class TotalCharacters(StatTrigger):
    def __init__(self):
        self.chars = 0

    def on_add_message(self, msg):
        if msg.content != None:
            self.chars += len(msg.content)
    
    def sumup(self):
        return "{} total characters".format(self.chars)

class CharsPerMessages(TotalMessages, TotalCharacters):
    def __init__(self):
        TotalMessages.__init__(self)
        TotalCharacters.__init__(self)

    def on_add_message(self, msg):
        TotalMessages.on_add_message(self, msg)
        TotalCharacters.on_add_message(self, msg)

    def sumup(self):
        return "{} char / msg".format(math.floor(self.chars / self.nb * 100) / 100)

class MessagesPerDay(TotalMessages):
    def __init__(self):
        super().__init__()
        self.first = None
        self.last = None

    def on_set_first_last(self, first, last):
        super().on_set_first_last(first, last)
        self.first = first
        self.last = last

    def sumup(self):
        day = 1000 * 60 * 60 * 24
        days = (self.last.ts - self.first.ts) / day
        return "{} msg / day".format(self.nb // days)

class TotalEmojis(StatTrigger):
    def __init__(self):
        self.emojis = 0

    def on_add_emoji(self, emoji):
        self.emojis += 1

    def sumup(self):
        return "{} total emojis".format(self.emojis)

class EmojisPerMessage(TotalMessages, TotalEmojis):
    def __init__(self):
        TotalMessages.__init__(self)
        TotalEmojis.__init__(self)

    def on_add_message(self, msg):
        TotalMessages.on_add_message(self, msg)
    
    def on_add_emoji(self, emoji):
        TotalEmojis.on_add_emoji(self, emoji)

    def sumup(self):
        return "{} emojis / msg".format(math.floor(self.emojis / self.nb * 100) / 100)

class ConversationStarts(StatTrigger):
    def __init__(self):
        self.last = None
        self.starts = 0

    def on_add_message(self, msg):
        if self.last == None:
            self.last = msg
            self.starts = 1
            return
        hour = 1000 * 60 * 60
        if msg.ts > self.last.ts + hour:
            self.starts += 1
        self.last = msg

    def sumup(self):
        return "{} conversation starts".format(self.starts)

class MostUsedEmojis(StatTrigger):
    def __init__(self):
        self.emojis = {}

    def on_add_emoji(self, emoji):
        if emoji not in self.emojis:
            self.emojis[emoji] = 0
        self.emojis[emoji] += 1
    
    def sumup(self):
        most_used = sorted(self.emojis, key=self.emojis.get, reverse=True)[:3]
        mu = {}
        for m in most_used:
            mu[m] = self.emojis[m]
        return "{} most used emojis".format(mu)

class MostUsedWord(StatTrigger):
    def __init__(self):
        self.words = {}

    def on_add_message(self, message):
        if message.content == None:
            return
        stripped = re.sub(r'\W+', " ", message.content).lower()
        words = [w for w in stripped.split(" ") if len(w) > 3]
        for word in words:
            if word not in self.words:
                self.words[word] = 0
            self.words[word] += 1
    
    def sumup(self):
        most_used = sorted(self.words, key=self.words.get, reverse=True)[1:6]
        mu = {}
        for m in most_used:
            mu[m] = self.words[m]
        return "{} most used words".format(mu)
