#import discord
#from discord.ext import commands
from enum import Enum
from random import shuffle, choice
from collections import Counter
import pickle
from copy import copy, deepcopy

class Card:
    def __init__(self, text, play=1, draw=0):
        self.text = text
        self.play = int(play)
        self.draw = int(draw)

BLACK_DECK = None
with open("cah/decks/uk_black.txt") as f:
    BLACK_DECK = tuple([Card(*line.strip('\n').split('|')) for line in f])

WHITE_DECK = None
with open("cah/decks/uk_white.txt") as f:
    WHITE_DECK = tuple([Card(*line.strip('\n').split('|')) for line in f])

class Player:
    def __init__(self, **kwargs):
        self.game = kwargs["game"]
        self.name = kwargs["name"]
        self.hand = []
        self.played = []
        self.score = 0

    def reset(self):
        self.played = []
        self.score = 0
        self.hand = []

    def is_tsar(self):
        return self.game.tsar is self

    def deal(self, n):
        self.hand += [self.game.white_deck.pop() for i in range(n)]

    def refresh_hand(self):
        self.deal(self.game.rules["hand_size"] - len(self.hand))

    def status(self):
        res = "You have {0.score} points.\n".format(self)
        if self.is_tsar():
            res += "You are the Card Tsar for this round.\n"
        res += "Your cards are:\n"
        for n, card in enumerate(self.hand):
            res += "{0:2}: {1.text}\n".format(n, card)
        return res

    def play(self, n):
        if self.is_tsar():
            print("The Card Tsar cannot play any cards.")
            return
        if len(self.played) == self.game.black_card.play:
            print("Cannot play any additional cards")
            return
        if n < 0 or n >= len(self.hand):
            print("Not a valid card.")
            return
        self.played.append(self.hand.pop(n))

    def clear(self):
        if not self.played:
            return
        for card in self.played:
            self.hand.append(card)
        self.played = []

    def vote(self, player):
        if not self.is_tsar():
            print("Only the Card Tsar can vote.")
            return
        if not self.game.all_played():
            print("Hold on, not everyone has played yet!")
            return
        if player is self:
            print("You can't vote for yourself!")
            return
        self.game.declare_winner(player)

class Game:
    def __init__(self):
        self.turn = 0
        self.players = {}
        self.white_deck = list(WHITE_DECK)
        self.black_deck = list(BLACK_DECK)
        self.black_card = None
        self.tsar = None
        self.rules = { "hand_size" : 10 }
        self.reset()
        
    def save(self, filename):
        with open(filename, mode='w+b') as f:
            pickle.dump(self, f)

    def load(self, filename):
        try:
            with open(filename, mode='r+b') as f:
                loaded = pickle.load(f)
                return loaded
        except FileNotFoundError:
            pass

    def status(self):
        if not self.tsar:
            res =  "The game has not started yet. Please assign a Card Tsar to start.\n"
            if self.players:
                res += "Players:\n"
                for p in self.players.values():
                    res += p.name + '\n'
            return res
        res = """Turn {0.turn}.
{0.tsar.name} is the Card Tsar.
The Black Card is: '{0.black_card.text}'\n""".format(self)
        for _, player in self.players.items():
            if self.tsar is player:
                played_str = "Card Tsar"
            elif not self.all_played():
                pending = self.black_card.play - len(player.played)
                played_str = "Waiting for {} card{}".format(pending, '' if pending==1 else 's')
            else:
                played_str = ", ".join([c.text for c in player.played])
            res += "{0.name:20} | {0.score:3} points | {1}\n".format(player, played_str)
        return res

    def reset(self):
        self.turn = 0
        self.white_deck = list(WHITE_DECK)
        shuffle(self.white_deck)
        self.black_deck = list(BLACK_DECK)
        shuffle(self.black_deck)
        for player in self.players.values():
            player.reset()
            player.refresh_hand()
        self.new_black_card()

    def add_player(self, player):
        self.players[player] = Player(name=str(player.name), game=self)
        self.players[player].refresh_hand()

    def remove_player(self, player):
        del self.players[player]

    def choose_tsar(self, player):
        self.tsar = player
        player.clear()

    def all_played(self):
        return all([len(p.played) == self.black_card.play for p in self.players.values() if not (p is self.tsar)])

    def declare_winner(self, winner):
        winner.score += 1
        self.turn += 1
        for player in self.players.values():
            player.refresh_hand()
            player.played = []
        self.new_black_card()
        self.choose_tsar(winner)

    def new_black_card(self):
        self.black_card = self.black_deck.pop()
        for player in self.players.values():
            player.deal(self.black_card.draw)
