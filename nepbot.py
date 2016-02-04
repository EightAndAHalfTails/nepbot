import discord
import asyncio
import random

client = discord.Client()

@client.event
@asyncio.coroutine
def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
@asyncio.coroutine
def roll(cmd, user):
    try:
        num = int(cmd.split('d')[0])
        sides = int(cmd.split('d')[1])
        print("Rolling {} {}-sided dice...".format(num,sides))
        results = [ random.randint(1,sides) for i in range(num) ]
        response = "_Rolling for {}_ `({})` ```{} ({})```".format(user.mention, cmd, sum(results), " + ".join(map(str, results)))
        return response
    except:
        return "Roll Failed"

@client.event
@asyncio.coroutine
def on_message(message):
    print("Message recieved: {}".format(message.content))
    if client.user in message.mentions:
        print("That's me!")
        cmd = message.content.replace("<@{}>".format(client.user.id),"").strip()
        print("I'm being told to '{}'".format(cmd))
        if cmd.startswith("roll "):
            res = yield from roll(cmd[5:], message.author)
            yield from client.send_message(message.channel, res)

client.run('jakebhumphrey@gmail.com', 'nepnepnishiteageru')
