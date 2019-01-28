import numpy as np
import re
import os


class MCBot():

    def __init__(self):
        self.word_list = [] # list of all words passed
        self.word_dict = {} # dict of (w1, w2) -> w3 mappings
        self.word_count = len(self.word_list)
        self.special_char = 'SPECCHAR'

    def train(self, file_name=''):
        """
        Train the MC Bot on a text (txt, csv, etc.) located in the
        /data directory. Updates the word list and word dict.
        """
        if file_name == '':
            self.word_dict = {}
        else: # need to add try/except block here
            dir = os.path.dirname(__file__)
            rel_path = 'data\\' + file_name
            abs_path = os.path.join(dir, rel_path)
            with open(abs_path) as f:
                words = f.read().split()
                f.close()
            self.update_dict(words)

    def add_text(self, text):
        """
        Adds a new string to the word list and word dict.
        """
        new_text = text.split()
        self.word_list.extend(new_text)
        self.update_dict(new_text)
        self.word_count = len(self.word_list)
    # changing to version 1, simply copy and paste from before to restore

    def update_dict(self, word_list):
        """
        Updates the word dict by taking in a list of words. The list is parsed
        into sequences of 3.  The dict stores keys that are pairs of consecutive words
        (w1, w2) and values that are the third consecutive word.

        For example, 'The dog barked loudly' would be
        parsed into (The, dog, barked) and (dog, barked, loudly), and stored as
        {('The', 'dog'): {'barked': 1}, ('dog', 'barked'): {'loudly': 1}}
        """
        result = self.word_dict
        for i in range(0, len(word_list) - 1):
            w1 = word_list[i]
            w2 = word_list[i + 1]


            if w1 not in result:
                result[w1] = {w2: 1}
            if w2 not in result[w1]:
                result[w1][w2] = 1
            else:
                result[w1][w2] = result[w1][w2] + 1

    def next_word(self, key, alpha=.1):
        """ Return a random word based on the current key (w1, w2)
        If the word is not present, then return a random word from the word_dict.
        If self.word_dict is empty, then return empty string.

        alpha is a tuning parameter that adjusts how often the bot will
        terminate if a key is not found in the dict.
        """
        if self.word_dict == dict():
            return ''
        if key not in self.word_dict:
            if np.random.uniform() < alpha:
                return self.special_char
            else:
                key = self.random_key()
        weights = np.array(list(self.word_dict[key].values()))
        weight_proba = weights / sum(weights)
        return np.random.choice(list(self.word_dict[key].keys()), p=weight_proba)


    def random_key(self):
        """
        Assumes that word_dict.keys() contains keys, and convert to list.
        This is necessary since np.random.choice cannot select from a list of tuples
        The other solution is to use random.choice, but that requires storing actual word values rather than counts.
        """
        key_list = list(self.word_dict.keys())
        rand_index = np.random.choice(len(key_list))
        return key_list[rand_index]

    def generate_sentence(self, word_limit=20, cap_first=True, end_punc='.'):
        """
        cap_first capitalizes the first word of the sentence, while end_punc allows
        customization of a punctuation mark to be added to the end of each sentence.
        """
        if self.word_dict == {}:
            print('Error: The bot hasn\'t been trained yet.')
            return ''
        punc = {'.', '?', '!', ';', ':', ',', end_punc}
        sentence = []

        seed = np.random.randint(0, len(self.word_list))
        curr = self.word_list[seed]
        if cap_first:
            sentence.append(curr.capitalize())
        else:
            sentence.append(curr)

        while len(sentence) <= word_limit:
            curr = self.next_word(curr)
            if curr == self.special_char:
                break
            else:
                sentence.append(curr)
        result = ' '.join(sentence)
        if end_punc != '' and result[-1] not in punc:
            result += end_punc
        return result


class MCBot2():
    """
    MCBot2 is uses an order-2 markov chain. This is not good OOP design, but it's functional
    for now.
    """
    def __init__(self):
        self.word_list = [] # list of all words passed
        self.word_dict = {} # dict of (w1, w2) -> w3 mappings
        self.word_count = len(self.word_list)

    def train(self, file_name=''):
        """
        Train the MC Bot on a text (txt, csv, etc.) located in the
        /data directory. Updates the word list and word dict.
        """
        if file_name == '':
            self.word_dict = {}
        else: # need to add try/except block here
            dir = os.path.dirname(__file__)
            rel_path = 'data\\' + file_name
            abs_path = os.path.join(dir, rel_path)
            with open(abs_path) as f:
                words = f.read().split()
                f.close()
            self.update_dict(words)

    def add_text(self, text):
        """
        Adds a new string to the word list and word dict.
        """
        new_text = text.split()
        self.word_list.extend(new_text)
        self.update_dict(new_text)

    def update_dict(self, word_list):
        """
        Updates the word dict by taking in a list of words. The list is parsed
        into sequences of 3.  The dict stores keys that are pairs of consecutive words
        (w1, w2) and values that are the third consecutive word.

        For example, 'The dog barked loudly' would be
        parsed into (The, dog, barked) and (dog, barked, loudly), and stored as
        {('The', 'dog'): {'barked': 1}, ('dog', 'barked'): {'loudly': 1}}
        """
        result = self.word_dict
        for i in range(0, len(word_list) - 2):
            w1 = word_list[i]
            w2 = word_list[i + 1]
            key = (w1, w2)
            value = word_list[i + 2]

            if key not in result:
                result[key] = {value: 1}
            if value not in result[key]:
                result[key][value] = 1
            else:
                result[key][value] = result[key][value] + 1

    def next_word(self, key, alpha=.1):
        """ Return a random word based on the current key (w1, w2)
        If the word is not present, then return a random word from the word_dict.
        If self.word_dict is empty, then return empty string.

        alpha is a tuning parameter that adjusts how often the bot will
        terminate if a key is not found in the dict.
        """
        if self.word_dict == dict():
            return ''
        if key not in self.word_dict:
            if np.random.uniform() < alpha:
                return self.special_char
            else:
                key = self.random_key()
        weights = np.array(list(self.word_dict[key].values()))
        weight_proba = weights / sum(weights)
        return np.random.choice(list(self.word_dict[key].keys()), p=weight_proba)


    def random_key(self):
        """
        Assumes that word_dict.keys() contains keys, and convert to list.
        This is necessary since np.random.choice cannot select from a list of tuples
        The other solution is to use random.choice, but that requires storing actual word values rather than counts.
        """
        key_list = list(self.word_dict.keys())
        rand_index = np.random.choice(len(key_list))
        return key_list[rand_index]

    def generate_sentence(self, word_limit=20, cap_first=True, end_punc='.'):
        """
        cap_first capitalizes the first word of the sentence, while end_punc allows
        customization of a punctuation mark to be added to the end of each sentence.
        """
        if self.word_dict == {}:
            print('Error: The bot hasn\'t been trained yet.')
            return ''
        punc = {'.', '?', '!', ';', ':', ',', end_punc}
        stop_chars = {'.', '?', '!', end_punc}
        sentence = []

        curr, next = self.random_key()
        if cap_first:
            sentence.append(curr.capitalize())
        else:
            sentence.append(curr)
        sentence.append(next)

        while len(sentence) <= word_limit:
            key = (curr, next)
            curr, next = next, self.next_word(key)
            sentence.append(next)
            if next[-1] in stop_chars:
                if np.random.uniform() < .5:
                    break

        result = ' '.join(sentence)
        if end_punc != '' and result[-1] not in punc:
            result += end_punc
        return result

