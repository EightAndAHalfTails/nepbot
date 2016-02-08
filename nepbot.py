import discord
from discord.ext import commands
import asyncio
from parse import parse
from random import randint, choice

from credentials import email, passw

desc = "The Protagonist of all Discord bots!"

nepbot = commands.Bot(command_prefix=commands.when_mentioned, description=desc)

@nepbot.event
@asyncio.coroutine
def on_ready():
    print('Logged in as')
    print(nepbot.user.name)
    print(nepbot.user.id)
    print('------')

def _roll(num, sides, mod=0):
    print("Rolling {}d{}+{}".format(num, sides, mod))
    res =[ randint(1,sides) for i in range(num) ]
    if mod:
        res += [mod]
    return res
    
@nepbot.command(description="Rolls dice given in NdN+N format.", brief="Rolls dice.")
@asyncio.coroutine
def roll(*cmd : str):
    cmd = "".join(cmd)
    r = parse("{num:d}d{sides:d}",cmd)
    if r:
        results = _roll(r['num'], r['sides'])
    else:
        r = parse("{num:d}d{sides:d}{mod:d}",cmd)
        if r:
            print(r)
            results = _roll(r['num'], r['sides'], r['mod'])
        else:
            yield from nepbot.reply("Please give me a command in in NdN+N format!")
            return
    yield from nepbot.reply("`({})` ```{} ({})```".format(cmd, sum(results), " + ".join(map(str, results))))
    

@nepbot.command(aliases=["pick"], description="Picks the <adj> out of [choices] (comma-separated)", brief="Let the hand of Nep decide...")
@asyncio.coroutine
def choose(adj:str, *choices:str):
    print(adj, choices)
    try:
        choices = [c.strip() for c in " ".join(choices).split(',')]
        print("Picking from {}".format(choices))
        res = choice(choices)
        print ("I choose {}".format(res))
        yield from nepbot.reply("{} is the {}!".format(res, adj).capitalize())
    except:
        yield from nepbot.reply("I can't decide!")

@nepbot.command(aliases=["join"], help="Accepts an invite to a Discord server.")
@asyncio.coroutine
def accept(invite_url:str):
    try:
        yield from nepbot.accept_invite(invite_url)
        yield from nepbot.reply("Thanks!")
    except:
        yield from nepbot.reply("It didn't work...")

@nepbot.command(pass_context=True, help="Picks one of the users in a given Role")
@asyncio.coroutine
def delegate(ctx, *role:str):
    role = " ".join(role).lower()
    print(role)
    try:
        usrs = [ u for u in ctx.message.server.members if role in [r.name.lower() for r in u.roles] ]
        res = choice(usrs)
        print("I choose {0.name}!".format(res))
        yield from nepbot.say("I choose {0.mention}!".format(res))
    except:
        yield from nepbot.say("That's not a real role!")

@nepbot.command(pass_context=True, help="Try to capture a Pokemon in PTU")
@asyncio.coroutine
def capture(ctx):
    message = ctx.message
    cr = 100
    while(True):
        yield from nepbot.reply("What is your level?")
        msg = yield from nepbot.wait_for_message(author=message.author)
        try:
            cr += int(msg.content)
            break
        except:
            yield from nepbot.reply("Sorry, what?")

    while(True):
        yield from nepbot.reply("What is the Pokemon's level?")
        msg = yield from nepbot.wait_for_message(author=message.author)
        try:
            cr -= 2*int(msg.content)
            break
        except:
            yield from nepbot.reply("Sorry, what?")

    while(True):
        yield from nepbot.reply("""Pick one of the following:```
1: The Pokemon is at more than 75% Hit Points.
2: The Pokemon is at 75% Hit Points or lower.
3: The Pokemon is at 50% Hit Points or lower.
4: The Pokemon is at 25% Hit Points or lower.
5: The Pokemon is at exactly 1 Hit Point.```""")
        msg = yield from nepbot.wait_for_message(author=message.author)
        try:
            cr -= [30, 15, 0, -15, -30][int(msg.content)-1]
            break
        except:
            yield from nepbot.reply("Sorry, what?")

    while(True):
        yield from nepbot.reply("How many evolutions does the Pokemon have remaining?")
        msg = yield from nepbot.wait_for_message(author=message.author)
        try:
            cr += [-10, 0, 10][int(msg.content)]
            break
        except:
            yield from nepbot.reply("Sorry, what?")

    while(True):
        yield from nepbot.reply("Is the Pokemon Shiny?")
        msg = yield from nepbot.wait_for_message(author=message.author)
        if msg.content.lower() in ['y', "yes"]:
            cr -= 10
            break
        elif msg.content.lower() in ['n', "no"]:
            break
        else:
            yield from nepbot.reply("Sorry, what?")
            
    while(True):
        yield from nepbot.reply("Is the Pokemon Legendary?")
        msg = yield from nepbot.wait_for_message(author=message.author)
        if msg.content.lower() in ['y', "yes"]:
            cr -= 30
            break
        elif msg.content.lower() in ['n', "no"]:
            break
        else:
            yield from nepbot.reply("Sorry, what?")

    while(True):
        yield from nepbot.reply("How many Persistant Status Afflictions (including Stuck) does the Pokemon have?")
        msg = yield from nepbot.wait_for_message(author=message.author)
        try:
            cr+= 10* int(msg.content)
            break
        except:
            yield from nepbot.reply("Sorry, what?")
        
    while(True):
        yield from nepbot.reply("How many Injuries or Volatile Status Afflictions (including Trapped) does the Pokemon have?")
        msg = yield from nepbot.wait_for_message(author=message.author)
        try:
            cr+= 5* int(msg.content)
            break
        except:
            yield from nepbot.reply("Sorry, what?")

    while(True):
        yield from nepbot.reply("Did you crit the Accuracy Check?")
        msg = yield from nepbot.wait_for_message(author=message.author)
        if msg.content.lower() in ['y', "yes"]:
            cr += 10
            break
        elif msg.content.lower() in ['n', "no"]:
            break
        else:
            yield from nepbot.reply("Sorry, what?")

    while(True):
        yield from nepbot.reply("Enter any other Bonuses as a positive number")
        msg = yield from nepbot.wait_for_message(author=message.author)
        try:
            cr += int(msg.content)
            break
        except:
            yield from nepbot.reply("Sorry, what?")

    yield from nepbot.reply("The Capture Rate is `{}`!".format(cr))
    res = sum(_roll(1, 100))
    success = res == 100 or res <= cr
    result  = "succeeded!" if success else "failed..."
    yield from nepbot.reply("You {} `({})`".format(result, res))
    return success
    
nepbot.run(email, passw)
