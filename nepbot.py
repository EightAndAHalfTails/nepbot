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
def cmd_choose(choices, adj):
    try:
        choices = [c.strip() for c in choices.split(',')]
        res = choice(choices)
        print("I choose {}".format(res))
        return "{} is {}!".format(res, adj).capitalize()
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
def cmd_pickfromrole(srv, role):
    try:
        usrs = [ u for u in srv.members if role in [r.name.lower() for r in u.roles] ]
        res = choice(usrs)
        print("I choose {0.name}!".format(res))
        return "I choose {0.mention}!".format(res)
    except:
        return "That's not a real role!"

@client.event
@asyncio.coroutine
def cmd_capture(message):
    cr = 100
    while(True):
        yield from client.send_message(message.channel, "What is your level?")
        msg = yield from client.wait_for_message(author=message.author)
        try:
            cr += int(msg.content)
            break
        except:
            yield from client.send_message(message.channel, "Sorry, what?")

    while(True):
        yield from client.send_message(message.channel, "What is the Pokemon's level?")
        msg = yield from client.wait_for_message(author=message.author)
        try:
            cr -= 2*int(msg.content)
            break
        except:
            yield from client.send_message(message.channel, "Sorry, what?")

    while(True):
        yield from client.send_message(message.channel, """Pick one of the following:```
1: The Pokemon is at more than 75% Hit Points.
2: The Pokemon is at 75% Hit Points or lower.
3: The Pokemon is at 50% Hit Points or lower.
4: The Pokemon is at 25% Hit Points or lower.
5: The Pokemon is at exactly 1 Hit Point.```""")
        msg = yield from client.wait_for_message(author=message.author)
        try:
            cr -= [30, 15, 0, -15, -30][int(msg.content)-1]
            break
        except:
            yield from client.send_message(message.channel, "Sorry, what?")

    while(True):
        yield from client.send_message(message.channel, "How many evolutions does the Pokemon have remaining?")
        msg = yield from client.wait_for_message(author=message.author)
        try:
            cr += [-10, 0, 10][int(msg.content)]
            break
        except:
            yield from client.send_message(message.channel, "Sorry, what?")

    while(True):
        yield from client.send_message(message.channel, "Is the Pokemon Shiny?")
        msg = yield from client.wait_for_message(author=message.author)
        if msg.content.lower() in ['y', "yes"]:
            cr -= 10
            break
        elif msg.content.lower() in ['n', "no"]:
            break
        else:
            yield from client.send_message(message.channel, "Sorry, what?")
            
    while(True):
        yield from client.send_message(message.channel, "Is the Pokemon Legendary?")
        msg = yield from client.wait_for_message(author=message.author)
        if msg.content.lower() in ['y', "yes"]:
            cr -= 30
            break
        elif msg.content.lower() in ['n', "no"]:
            break
        else:
            yield from client.send_message(message.channel, "Sorry, what?")

    while(True):
        yield from client.send_message(message.channel, "How many Persistant Status Afflictions (including Stuck) does the Pokemon have?")
        msg = yield from client.wait_for_message(author=message.author)
        try:
            cr+= 10* int(msg.content)
            break
        except:
            yield from client.send_message(message.channel, "Sorry, what?")
        
    while(True):
        yield from client.send_message(message.channel, "How many Injuries or Volatile Status Afflictions (including Trapped) does the Pokemon have?")
        msg = yield from client.wait_for_message(author=message.author)
        try:
            cr+= 5* int(msg.content)
            break
        except:
            yield from client.send_message(message.channel, "Sorry, what?")

    while(True):
        yield from client.send_message(message.channel, "Did you crit the Accuracy Check?")
        msg = yield from client.wait_for_message(author=message.author)
        if msg.content.lower() in ['y', "yes"]:
            cr += 10
            break
        elif msg.content.lower() in ['n', "no"]:
            break
        else:
            yield from client.send_message(message.channel, "Sorry, what?")

    while(True):
        yield from client.send_message(message.channel, "Enter any other Bonuses as a positive number")
        msg = yield from client.wait_for_message(author=message.author)
        try:
            cr += int(msg.content)
            break
        except:
            yield from client.send_message(message.channel, "Sorry, what?")

    yield from client.send_message(message.channel, "The Capture Rate is `{}`!".format(cr))
    res = sum(roll(1, 100))
    success = res == 100 or res <= cr
    result  = "succeeded!" if success else "failed..."
    yield from client.send_message(message.channel, "You {} `({})`".format(result, res))
    return success
    
    
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
            res = yield from cmd_choose(parsed_cmd['list'], parsed_cmd['adj'])
            yield from client.edit_message(tmp, res)
        parsed_cmd = parse("accept {inv}", cmd)
        if parsed_cmd:
            print("I'm being given an invite!")
            res = yield from cmd_accept(parsed_cmd['inv'])
            yield from client.send_message(message.author, res)
        parsed_cmd = parse("pick one of the {role}",cmd)
        if parsed_cmd:
            print("That's a pickfromrole command!")
            yield from client.send_message(message.channel, "I have to pick, huh?")
            tmp = yield from client.send_message(message.channel, "Hmm...")
            res = yield from cmd_pickfromrole(message.server, parsed_cmd['role'])
            yield from client.edit_message(tmp, res)
        if cmd == "capture":
            print("That's a capture command!")
            yield from cmd_capture(message)
        

client.run('jakebhumphrey@gmail.com', 'nepnepnishiteageru')
