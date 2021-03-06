import discord
from discord.ext import commands
import asyncio
from parse import parse
from random import randint, choice
from datetime import date
import requests
from lxml import html
from credentials import tokens, ids, irclogdir
from gtts import gTTS
from tempfile import TemporaryFile
from time import sleep
import os
import io
from dice import roll as diceroll, parse

desc = "The Protagonist of all Discord bots!"

nepbot = commands.Bot(command_prefix=commands.when_mentioned, description=desc)

@nepbot.event
async def on_ready():
    print('Logged in as')
    print(nepbot.user.name)
    print(nepbot.user.id)
    print('------')

def _getError():
    return choice(["What?", "Wait, what?", "I don't get it...", "Huh?", "I don't understand...", "Could you repeat that?", "What's that supposed to mean?", "That can't be right...", "Uhhh, what?", "Did you mess up or something?", "Sorry, what?" ])

def _getExplicitive():
    return choice(["goodness", "fuck", "oh, no", "oh, dear", "oh my god", "neppu", "shit", "wtf", "bullshit", "damn", "dammit", "goddammit", "crap", "darn", "oh, darn", "oh", "omg", "no way", "balls", "bollocks" ])

@nepbot.command(description="Rolls dice given in NdN+N format.", brief="Rolls dice.", aliases=["r"])
async def roll(*cmd : str):
    cmd = "".join(cmd)
    try:
        res = parse(cmd)
        await nepbot.reply("`({})` ```{} ({})```".format(cmd, res.result, res.rollstr))
    except Exception as e:
        if str(e) is not "":
            await nepbot.reply(str(e))
        else:
            await nepbot.reply(_getError().lower())

@nepbot.command(description="Rolls dice with OVA rules. Provide the modifier as an argument.", brief="Rolls dice in the OVA system.", aliases=["or"])
async def ovaroll(modifier : int):
    try:
        if modifier >= 0:
            rolls = [ diceroll(6).result for i in range(2+modifier) ]
            results = [ sum([ x for x in rolls if x == i]) for i in [1,2,3,4,5,6] ]
            rollstr = str(sorted(rolls))
            res = max(results)
        else:
            rolls = [ diceroll(6).result for i in range(abs(modifier)) ]
            rollstr = str(sorted(rolls))
            res = min(rolls)
        await nepbot.reply("```{} ({})```".format(res, rollstr))
    except Exception as e:
        if str(e) is not "":
            await nepbot.reply(str(e))
        else:
            await nepbot.reply(_getError().lower())        

@nepbot.command(aliases=["pick"], description="Picks the <adj> out of [choices] (comma-separated)", brief="Let the hand of Nep decide...")
async def choose(adj:str, *choices:str):
    print(adj, choices)
    try:
        choices = [c.strip() for c in " ".join(choices).split(',')]
        print("Picking from {}".format(choices))
        res = choice(choices)
        print ("I choose {}".format(res))
        await nepbot.reply("{} is the {}!".format(res, adj).capitalize())
    except:
        await nepbot.reply("I can't decide!")

@nepbot.command(aliases=["join"], help="Generates a URL to allow me onto a server that you manage")
async def invite():
    await nepbot.reply("https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=536870911".format(ids["nep"]))

#@nepbot.command(pass_context=True, help="leaves a server.")
#async def leave(ctx):
#    await nepbot.say("Goodbye!")
#    await nepbot.leave_server(ctx.message.server)

@nepbot.command(pass_context=True, help="Picks one of the users in a given Role")
async def delegate(ctx, *role:str):
    role = " ".join(role).lower()
    print(role)
    try:
        usrs = [ u for u in ctx.message.server.members if role in [r.name.lower() for r in u.roles] ]
        res = choice(usrs)
        print("I choose {0.name}!".format(res))
        await nepbot.say("I choose {0.mention}!".format(res))
    except:
        await nepbot.say("That's not a real role!")

last_params = {}
async def _capt(**kwargs):
    for key in kwargs:
        last_params[key] = kwargs[key]

    cr = 10 + sum(last_params.values())
    await nepbot.reply("The Capture Rate is `{}`!".format(cr))
    res = diceroll(20).result
    success = res == 20 or res >= cr
    for shakes, check in [("once", res-cr > 3), ("twice", res-cr > 2), ("thrice", res-cr > 1)]:
        nepbot.type()
        await asyncio.sleep(1)
        if check:
            await nepbot.reply("Shook {}...".format(shakes))
        else:
            await nepbot.reply("{}! The Pokemon broke free...".format(_getExplicitive().capitalize()))
            return
    nepbot.type()
    await asyncio.sleep(1)
    if success:
        await nepbot.reply("Gotcha! The Wild Pokemon was caught! `({})`".format(res))
    else:
        await nepbot.reply("{}! The Pokemon broke free... ({})".format(_getExplicitive().capitalize(), res))

@nepbot.command(pass_context=True, help="Try to capture a Pokemon in PTU")
async def capture(ctx):
    message = ctx.message
    params = {}
    while(True):
        await nepbot.reply("""What Trainer Title do you have?```
1: No Title
2: Amateur Trainer (LV 5)
3: Capable Trainer (LV 10)
4: Veteran Trainer (LV 20)
5: Elite Trainer   (LV 30)
6: Champion        (LV 40)```""")
        msg = await nepbot.wait_for_message(author=message.author, channel=message.channel)
        if msg.content.lower() in ["s", "same"]:
            break
        try:
            resp = int(msg.content)-1
            assert 0<=resp<=5
            params["lv"] = -resp
            break
        except:
            await nepbot.reply(_getError())

    while(True):
        await nepbot.reply("What is the Pokemon's level?")
        msg = await nepbot.wait_for_message(author=message.author, channel=message.channel)
        if msg.content.lower() in ["s", "same"]:
            break
        try:
            params["elv"] = int(msg.content)//10
            break
        except:
            await nepbot.reply(_getError())

    while(True):
        await nepbot.reply("""Pick one of the following:```
1: The Pokemon is at more than 50% Hit Points.
2: The Pokemon is at 50% Hit Points or lower.
3: The Pokemon is at 25% Hit Points or lower.```""")
        msg = await nepbot.wait_for_message(author=message.author, channel=message.channel)
        if msg.content.lower() in ["s", "same"]:
            break
        try:
            res = -(int(msg.content)-1)
            assert res in [0,-1,-2]
            params["hp"] = 2*res
            break
        except:
            await nepbot.reply(_getError())

    while(True):
        await nepbot.reply("How many evolutions does the Pokemon have remaining?")
        msg = await nepbot.wait_for_message(author=message.author, channel=message.channel)
        if msg.content.lower() in ["s", "same"]:
            break
        try:
            assert int(msg.content) in [0,1,2]
            params["evol"] = [0,-2,-6][int(msg.content)]
            break
        except:
            await nepbot.reply(_getError())

    while(True):
        await nepbot.reply("Does the Pokemon have 5 or more injuries?")
        msg = await nepbot.wait_for_message(author=message.author, channel=message.channel)
        if msg.content.lower() in ["s", "same"]:
            break
        if msg.content.lower() in ['y', "yes"]:
            params["inj"] = -4
            break
        elif msg.content.lower() in ['n', "no"]:
            params["inj"] = 0
            break
        else:
            await nepbot.reply(_getError())

    while(True):
        await nepbot.reply("Is the Pokemon suffering from at least one Persistant or Volatile Status Affliction?")
        msg = await nepbot.wait_for_message(author=message.author, channel=message.channel)
        if msg.content.lower() in ["s", "same"]:
            break
        if msg.content.lower() in ['y', "yes"]:
            params["stat"] = -2
            break
        elif msg.content.lower() in ['n', "no"]:
            params["stat"] = 0
            break
        else:
            await nepbot.reply(_getError())

    while(True):
        await nepbot.reply("Did you crit the Accuracy Check?")
        msg = await nepbot.wait_for_message(author=message.author, channel=message.channel)
        if msg.content.lower() in ["s", "same"]:
            break
        if msg.content.lower() in ['y', "yes"]:
            params["crit"] = -1
            break
        elif msg.content.lower() in ['n', "no"]:
            params["crit"] = 0
            break
        else:
            await nepbot.reply(_getError())

    while(True):
        await nepbot.reply("Enter any other Bonuses as a positive number")
        msg = await nepbot.wait_for_message(author=message.author, channel=message.channel)
        if msg.content.lower() in ["s", "same"]:
            break
        try:
            params["other"] = -int(msg.content)
            break
        except:
            await nepbot.reply(_getError())
    await _capt(**params)

@nepbot.command(help="Offers a glimpse into the Hyperdimension...")
async def scry():
    try:
        today = date.today()
        log = "{}/{}-{:02}-{:02}.log".format(irclogdir, today.year, today.month, today.day)
        with open(log) as f:
            await nepbot.say("`{}`".format(f.readlines()[-1]))
    except:
        await nepbot.say("Outlook unclear. Try again later.")

@nepbot.command(help="Posts an xkcd comic and hovertext")
async def xkcd(number:str=""):
    url = 'http://xkcd.com/{}'.format(number)
    try:
        page = requests.get(url)
        tree = html.fromstring(page.content)

        comic = tree.xpath('//div[@id="comic"]/img/attribute::src')[0]
        hover = tree.xpath('//div[@id="comic"]/img/attribute::title')[0]
        comic = requests.get("http:{}".format(comic)).content

        await nepbot.upload(io.BytesIO(comic), filename="xkcd-{}.png".format(number))
        await nepbot.say("_{}_".format(hover))

    except Exception as e:
        print(e)
        await nepbot.say(url)

@nepbot.command(help="Says something in a voice channel")
async def speak(server:str, channel:str, *message:str):
    chan = discord.utils.get(nepbot.get_all_channels(), server__name=server, name=channel, type=discord.ChannelType.voice)
    if not chan:
        await nepbot.say("I can't find that voice channel!")
        return

    sentence = " ".join(message)
    print(sentence)
    tts = gTTS(text=sentence, lang='ja')
    #f = TemporaryFile()
    #tts.write_to_fp(f)
    tts.save("nepsay.mp3")

    try:
        voice = await nepbot.join_voice_channel(chan)
        player = voice.create_ffmpeg_player("nepsay.mp3")
        #player = voice.create_ffmpeg_player(f, options="-v verbose", pipe=True) # TODO: get this to work

        player.start()
        while not player.is_done():
            await asyncio.sleep(1)
    except Exception as e:
        print(e)
        await nepbot.say("I failed...")
    finally:
        #f.close()
        try:
            os.remove("nepsay.mp3")
        except:
            pass
        await voice.disconnect()

nepbot.run(tokens["nep"])
