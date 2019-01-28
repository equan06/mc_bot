import socket
import time
import os
import mcbot as mcb
import re


class TwitchBot:
    def __init__(self, user, order=1, admin='', wait=45, post=True, write=True, refresh=True):
        self.user = user
        self.admin = admin
        self.channel = ''
        self.auth = ''
        self.port = 0
        self.host = ''
        self.order = order
        if self.order == 1:
            self.mc_bot = mcb.MCBot()
        else:
            self.mc_bot = mcb.MCBot2()
        self.s = socket.socket()
        self.encoding = 'utf-8'
        self.curr_time = time.time()
        self.last_time = self.curr_time
        self.read_buffer = ""
        self.post = post  # bot in posting mode
        self.write = write
        self.refresh = refresh
        self.online = False  # bot connected
        self.all_logs, self.markov_sentences = {}, {}
        self.msg_buffer = []
        self.msg_count, self.sentences_count = 0, 0
        # default wait time (seconds) between bot posts
        self.wait = wait
        self.word_limit = 20
        self.at_count = 0
        self.banned = self.read_banned()


    @staticmethod
    def get_user(line):
        line = re.search(r":.+?!", line)
        if line:
            return line.group(0)[1:-1]
        return ''

    @staticmethod
    def get_message(line):
        line = re.search(r" :.+", line)
        if line:
            return line.group(0)[2:]
        return ''

    @staticmethod
    def connected(line):
        return not ("End of /NAMES list" in line)

    @staticmethod
    def print_message(message):
        print(" ".join(['[BOT]', message]))

    @staticmethod
    def filter_at(message):
        """
        Filter message for '@' character.
        """
        return re.sub(r'@', '', message)

    @staticmethod
    def check_users(user):
        """
        Check if user is a specific user.
        In the future, read input from a .txt, but this is more convenient.
        """
        return (user == 'nightbot') | (user == 'scootycoolguy')

    @staticmethod
    def read_banned(file='banned.txt'):
        """
        Read a list of banned words from banned.txt. If not present, ignore
        """
        try:
            with open(file) as f:
                words = f.read()
            return re.split(r',', words)
        except FileNotFoundError:
            print("Alert: banned.txt not found. ")
            return ""

    def refresh_mc_bot(self):
        if self.order == 1:
            self.mc_bot = mcb.MCBot()
        else:
            self.mc_bot = mcb.MCBot2()

    def contains_banned(self, message):
        """
        Check message for banned words.
        """
        if self.banned == "":
            return False
        else:
            line = set(message.split(' '))
            for b in self.banned:
                if b in line:
                    return True
        return False

    def connect(self, host, port, auth, channel):
        """
        Connect to the IRC server specified by HOST, PORT, AUTH, and CHANNEL.
        These should be specified in auth.py
        """
        self.channel = channel
        self.host = host
        self.port = port
        self.auth = auth
        self.s.connect((host, port))
        self.s.send(f"PASS {auth} \r\n".encode(self.encoding))
        self.s.send(f"NICK {self.user} \r\n".encode(self.encoding))
        self.s.send(f"JOIN #{channel} + \r\n".encode(self.encoding))
        self.join()

    def join(self):
        """
        Join the server specified by CHANNEL.
        """
        read_buffer = ""
        connecting = True
        while connecting:
            read_buffer = read_buffer + self.s.recv(1024).decode()
            temp = str.split(read_buffer, "\n")
            read_buffer = temp.pop()
            for line in temp:
                print(line)
                connecting = self.connected(line)
        self.print_message(f'#{self.channel} joined')

    def send_message(self, message):
        """
        Send a message to the server.
        """
        message_temp = f"PRIVMSG #{self.channel} :{message}"
        self.s.send((message_temp + "\r\n").encode("utf-8"))
        self.print_message(f'sent: {message}')

    def check_admin(self, user, message):
        """
        Check if user is the dedicated admin account. Several commands can be run
        if detected in chat:

        - wait[seconds] will change the wait time to [seconds]
        - count will print total message count to console
        - write will toggle whether logs will be written upon shutdown
        - post will toggle post mode
        - limit[num] will limit the length of markov sentences to [num]
        - refresh will toggle refresh mode
        - status will print bot status to console
        - exit will shutdown the bot
        """
        if self.admin == '':
            return ''
        if user == self.admin:
            self.print_message(f'{user} detected: message was: {message}')
            if 'wait' in message:
                self.wait = int(message[4:])
                self.print_message(f'wait changed to {self.wait}')
            if 'count' in message:
                self.print_message(f'{self.msg_count}messages collected')
            if 'write' in message:
                self.write = not self.write
                self.print_message(f'write mode: {self.write}')
            if 'post' in message:
                self.post = not self.post
                self.print_message(f'post mode: {self.post}')
            if 'limit' in message:
                self.word_limit = int(message[5:])
                self.print_message(f'word limit changed to {self.word_limit}')
            if 'refresh' in message:
                self.refresh = not self.refresh
                self.print_message(f'refresh mode: {self.refresh}')
            if 'status' in message:
                self.status_update()
            if "exit" in message:
                self.online = False
                self.print_message('going offline')
                self.print_message(f'@ count was {self.at_count}')
                return 'exit'
            return ''

    def status_update(self):
        """
        Print bot status to console.
        """
        self.print_message(f'msg_count: {self.msg_count} at_count: {self.at_count}\n' +
                           f'post: {self.post} online: {self.online} refresh: {self.refresh} write: {self.write}\n' +
                           f'word_limit: {self.word_limit} wait: {self.wait}')

    def update_logs(self, message):
        """
        Update the the log of all collected messages and the message buffer for the markov bot.
        For now, disable the collection of all logs. Only use for debugging/data collection purposes.
        Note that the collection of chat logs is (probably) against Twitch TOS.
        """
        # self.all_logs[self.curr_time] = message
        self.msg_buffer.append(message)
        self.msg_count += 1

    def update_sentences(self, sentence):
        """
        Update the log of generated markov sentences.
        """
        self.markov_sentences[self.curr_time] = sentence
        self.sentences_count += 1

    def ready(self):
        """
        Check if <self.wait> time since the last bot posting.
        """
        return self.curr_time > self.last_time + self.wait

    def write_logs(self, file='logs.txt'):
        """
        Write collected chat logs to /data/logs/logs.txt.
        Currently, this function is never actually called, but
        is here for dev purposes.
        """
        if self.all_logs == {}:
            return
        time_str = time.strftime('%Y-%m-%d_%H_%M', time.localtime(time.time()))
        newpath = 'data\\logs\\'
        if not os.path.exists(newpath):
            os.makedirs(newpath)
        rel_path = ''.join([newpath, time_str, file])
        curr_dir = os.path.dirname(__file__)
        abs_path = os.path.join(curr_dir, rel_path)

        with open(abs_path, 'w', encoding=self.encoding) as f:
            f.write(str(self.all_logs))
        self.print_message(f'All logs written at {time_str}')

    def write_markov_sentences(self, file='markov.txt'):  # writes all generated sentences
        """
        Write generated markov sentences to /data/logs/markov.txt
        """
        time_str = time.strftime('%Y-%m-%d_%H-%M', time.localtime(time.time()))
        newpath = 'data\\logs\\'
        if not os.path.exists(newpath):
            os.makedirs(newpath)
        rel_path = ''.join([newpath, time_str, file])
        curr_dir = os.path.dirname(__file__)
        abs_path = os.path.join(curr_dir, rel_path)

        output = '\n\n'.join(list(self.markov_sentences.values()))
        with open(abs_path, 'w', encoding=self.encoding) as f:
            f.write(output)
        self.print_message(f'Markov sentences written at {time_str}')

    def shutdown(self):
        if self.write:
            # self.write_logs()
            self.write_markov_sentences()
        # close socket
        self.s.close()

    def run(self):
        self.last_time = time.time()
        self.online = True
        read_buffer = ""
        self.status_update()
        while self.online:
            try:
                # read from the socket input stream
                read_buffer = read_buffer + self.s.recv(1024).decode()
            except UnicodeDecodeError:
                self.print_message('UnicodeDecodeError: skipping line')
                continue
            current = str.split(read_buffer, "\n")
            read_buffer = current.pop()

            for line in current:
                # respond to PING afk check, which occurs at unknown time intervals
                if line == 'PING :tmi.twitch.tv':
                    self.s.send(("PONG" + "\r\n").encode(self.encoding))
                    self.print_message('PONG was sent.')
                    continue
                self.curr_time = time.time()
                user = self.get_user(line)
                message = self.get_message(line)

                # if someone @s the bot
                if self.user in message:
                    self.print_message(f'{user} @ed me. msg: {message}')
                    self.at_count += 1

                # skip message if contains banned words
                if self.contains_banned(message):
                    continue

                # prevent bot from @ing people
                message = self.filter_at(message)  
                
                # check if user is admin
                self.check_admin(user, message) 

                # end run loop
                if not self.online:
                    break

                if self.check_users(user):
                    continue
                else:
                    self.update_logs(message)

                # if bot is ready to post, then generate a markov sentence
                if self.ready():
                    while len(self.msg_buffer) > 0:
                        self.mc_bot.add_text(self.msg_buffer.pop())
                    sentence = self.mc_bot.generate_sentence(word_limit=self.word_limit,
                                        cap_first=True, end_punc='.')
                    self.curr_time = time.time()
                    self.last_time = self.curr_time

                    # if post mode is disabled, bot will print to console
                    if self.post:
                        self.send_message(sentence)
                    else:
                        self.print_message(sentence)
                    self.update_sentences(sentence)
                    if self.refresh:
                        self.refresh_mc_bot()
                        self.msg_buffer = []
        self.shutdown()
