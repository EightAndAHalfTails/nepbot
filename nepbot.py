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
        return res.capitalize()
    except:
        return "I can't decide!"

@client.event
@asyncio.coroutine
def cmd_accept(inv):
    try:
        yield from client.accept_invite(inv)
        return "Thanks!"
    except:
        return "It didn't work..."

@client.event
@asyncio.coroutine
def on_message(message):
    #print("Message recieved: {}".format(message.content))
    if client.user in message.mentions:
        print("That's me!")
        cmd = message.content.replace("<@{}>".format(client.user.id),"").strip().lower()
        print("I'm being told to '{}'".format(cmd))
        parsed_cmd = parse("roll {cmd}", cmd)
        if parsed_cmd:
            print("That's a roll command!")
            tmp = yield from client.send_message(message.channel, "Rolling...")
            res = yield from cmd_roll(parsed_cmd['cmd'], message.author)
            yield from client.edit_message(tmp, res)
        parsed_cmd = parse("which is {adj}:{list}?", cmd)
        if parsed_cmd:
            print("That's a choose command!")
            yield from client.send_message(message.channel, "I have to pick, huh?")
            tmp = yield from client.send_message(message.channel, "Hmm...")
            res = yield from cmd_choose(parsed_cmd['list'])
            yield from client.edit_message(tmp, "{} is {}!".format(res, parsed_cmd['adj']))
        parsed_cmd = parse("accept {inv}", cmd)
        if parsed_cmd:
            print("I'm being given an invite!")
            res = yield from cmd_accept(parsed_cmd['inv'])
            yield from client.send_message(message.author, res)

client.run('jakebhumphrey@gmail.com', 'nepnepnishiteageru')
