import discord
import asyncio
from parse import parse
from random import randint, choice

client = discord.Client()

@client.event
@asyncio.coroutine
def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

def roll(num, sides, mod=0):
    print("Rolling {}d{}+{}".format(num, sides, mod))
    res =[ randint(1,sides) for i in range(num) ]
    if mod:
        res += [mod]
    return res
    
@client.event
@asyncio.coroutine
def cmd_roll(cmd, user):
    cmd = cmd.replace(" ","")
    r = parse("{num:d}d{sides:d}",cmd)
    if r:
        results = roll(r['num'], r['sides'])
    else:
        r = parse("{num:d}d{sides:d}{mod:d}",cmd)
        if r:
            print(r)
            results = roll(r['num'], r['sides'], r['mod'])
        else:
            return "Please give me a command in in NdN+N format!"
    response = "_Rolling for {}_ `({})` ```{} ({})```".format(user.mention, cmd, sum(results), " + ".join(map(str, results)))
    return response

@client.event
@asyncio.coroutine
def cmd_choose(choices):
    try:
        choices = [c.strip() for c in choices.split(',')]
        res = choice(choices)
        print("I choose {}".format(res))
        return res
    except:
        return "I can't decide!"
    
@client.event
@asyncio.coroutine
def on_message(message):
    #print("Message recieved: {}".format(message.content))
    if client.user in message.mentions:
        print("That's me!")
        cmd = message.content.replace("<@{}>".format(client.user.id),"").strip().lower()
        print("I'm being told to '{}'".format(cmd))
        rollcmd = parse("roll {cmd}", cmd)
        if rollcmd:
            print("That's a roll command!")
            tmp = yield from client.send_message(message.channel, "Rolling...")
            res = yield from cmd_roll(rollcmd['cmd'], message.author)
            yield from client.edit_message(tmp, res)
        choosecmd = parse("which is {adj}: {list}?", cmd)
        if choosecmd:
            yield from client.send_message(message.channel, "I have to pick, huh?")
            tmp = yield from client.send_message(message.channel, "Hmm...")
            res = yield from cmd_choose(choosecmd['list'])
            yield from client.edit_message(tmp, "{} is {}!".format(res, choosecmd['adj']))

client.run('jakebhumphrey@gmail.com', 'nepnepnishiteageru')
