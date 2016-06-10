#import discord
#from discord.ext import commands
from enum import Enum
from random import shuffle, choice
from collections import Counter
import pickle

class Card:
    def __init__(self, text, draw=0, play=1):
        self.text = text
        self.draw = draw
        self.play = play

BLACK_DECK = tuple(map(Card, """Daddy, why is mummy crying?
__________. That's why mums go to Iceland.
I'm sorry, sir, but I couldn't complete my homework because of __________.
The TFL apologizes for the delay in train service due to ________.
When I am Prime Minister of the United Kingdom, I will create the Ministry of _______.""".split('\n')))

with open("black_deck", mode='w+b') as f:
    pickle.dump(BLACK_DECK, f)

WHITE_DECK = tuple(map(Card, """Germans on holiday.
The unstoppable tide of Islam.
A thousand Scottish warriors lifing their kilts in unison.
Druids.
A white van man.
A vindaloo poo.
Establishing dominance.
Doing a shit in Pudsey Bear's eyehole.
Blowing up Parliament
Blood, Toil, Tears, and sweat.
Anything that comes out of Prince Philip's mouth.
An argument with Richard Dawkins.
Cheating in the Paralympics.
Gentleman's Relish.
Buckfast Tonic Wine.
Dogging.
Wanking into a pool of Children's tears.
Wiping her bum.
A brain tumour.
David Bowie flying in on a tiger made of lightning.
The way James Bond treats women.
Tories.
Used knickers.
Waking up half-naked in a Little Chef car park.
A mad cow.""".split('\n')))

with open("white_deck", mode='w+b') as f:
    pickle.dump(WHITE_DECK, f)

class Deck(list):
    def draw(self, n):
        return [self.pop() for i in range(n)]

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
        self.hand += self.game.white_deck.draw(n)

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
        self.game.check_for_round_end()

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
        if self.game.phase == 0:
            print("You can only vote in the voting phase")
            return
        if player is self:
            print("You cannot vote for yourself.")
            return
        self.game.declare_winner(player)

class Game:
    def __init__(self, bot):
        self.turn = 0
        self.phase = 0
        self.players = {}
        with open("white_deck", mode='rb') as f:
            self.white_deck = Deck(pickle.load(f))
        with open("black_deck", mode='rb') as f:
            self.black_deck = Deck(pickle.load(f))
        self.black_card = None
        self.tsar = None
        self.bot = bot
        self.rules = { "hand_size" : 10 }

    def status(self):
        res = """It is the {1} phase of turn {0.turn}.
{0.tsar.name} is the Card Tsar.
The Black Card is: '{0.black_card.text}'\n""".format(self, ["playing", "voting"][self.phase])
        for player in self.players:
            if self.tsar is player:
                played_str = "Card Tsar"
            elif self.phase == 0:
                pending = self.black_card.play - len(player.played)
                played_str = "Waiting for {} card{}".format(pending, '' if pending==1 else 's')
            else:
                played_str = ", ".join([c.text for c in player.played])
            res += "{0.name:20} | {0.score:3} points | {1}\n".format(player, played_str)
        return res

    def reset(self):
        self.turn = 0
        self.phase = 0
        shuffle(self.white_deck)
        shuffle(self.black_deck)
        for _, player in self.players:
            player.reset()
            player.refresh_hand()
        self.choose_tsar()
        self.new_black_card()

    def add_player(self, player):
        self.players[player] = Player(name=str(player.name), game=self))

    def remove_player(self, player):
        del self.players[player]

    def choose_tsar(self, player=None):
        if player:
            self.tsar = player
            player.clear()
        elif self.players:
            self.tsar = choice(self.players)
            self.tsar.clear()
        else:
            self.tsar = None

    def check_for_round_end(self):
        all_played = all([len(p.played) == self.black_card.play for _, p in self.players if not (p is self.tsar)])
        if not all_played:
            return
        self.phase = 1
        print(self.status())

    def declare_winner(self, player):
        print("{.name} is declared the winner!".format(player))
        player.score += 1
        self.choose_tsar(player)
        self.turn += 1
        self.phase = 0
        for _, player in self.players:
            player.refresh_hand()
        self.new_black_card()
        print(self.status())

    def new_black_card(self):
        self.black_card = self.black_deck.pop()
        for _, player in self.players:
            player.deal(self.black_card.draw)

if __name__ == "__main__":
    g = Game(None)
    g.add_player("Luke The Human")
    g.add_player("EightAndAHalfTails")
    g.reset()
    print(g.status())
    for _, p in g.players:
        print(p.status())
    for _, p in g.players:
        p.play(0)
    for _, p in g.players:
        g.tsar.vote(p)
