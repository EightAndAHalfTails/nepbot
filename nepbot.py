import discord
from discord.ext import commands
import asyncio
from parse import parse
from random import randint, choice
from datetime import date
import requests
from lxml import html
from credentials import email, passw, irclogdir
from gtts import gTTS
from tempfile import TemporaryFile
from time import sleep
import os
import io
from dice import roll, parse

desc = "The Protagonist of all Discord bots!"

nepbot = commands.Bot(command_prefix=commands.when_mentioned, description=desc)

@nepbot.event
async def on_ready():
    print('Logged in as')
    print(nepbot.user.name)
    print(nepbot.user.id)
    print('------')

def _getError():
    return choice([ "What?", "Wait, what?", "I don't get it...", "Huh?", "I don't understand...", "Could you repeat that?", "What's that supposed to mean?", "That can't be right...", "Uhhh, what?", "Did you mess up or something?", "Sorry, what?" ])
    
@nepbot.command(description="Rolls dice given in NdN+N format.", brief="Rolls dice.")
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

@nepbot.command(aliases=["join"], help="Accepts an invite to a Discord server.")
async def accept(invite_url:str):
    try:
        await nepbot.accept_invite(invite_url)
        await nepbot.reply("Thanks!")
    except:
        await nepbot.reply("It didn't work...")

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

@nepbot.command(pass_context=True, help="Try to capture a Pokemon in PTU")
async def capture(ctx):
    message = ctx.message
    cr = 100
    while(True):
        await nepbot.reply("What is your level?")
        msg = await nepbot.wait_for_message(author=message.author)
        try:
            cr += int(msg.content)
            break
        except:
            await nepbot.reply(_getError())

    while(True):
        await nepbot.reply("What is the Pokemon's level?")
        msg = await nepbot.wait_for_message(author=message.author)
        try:
            cr -= 2*int(msg.content)
            break
        except:
            await nepbot.reply(_getError())

    while(True):
        await nepbot.reply("""Pick one of the following:```
1: The Pokemon is at more than 75% Hit Points.
2: The Pokemon is at 75% Hit Points or lower.
3: The Pokemon is at 50% Hit Points or lower.
4: The Pokemon is at 25% Hit Points or lower.
5: The Pokemon is at exactly 1 Hit Point.```""")
        msg = await nepbot.wait_for_message(author=message.author)
        try:
            cr -= [30, 15, 0, -15, -30][int(msg.content)-1]
            break
        except:
            await nepbot.reply(_getError())

    while(True):
        await nepbot.reply("How many evolutions does the Pokemon have remaining?")
        msg = await nepbot.wait_for_message(author=message.author)
        try:
            cr += [-10, 0, 10][int(msg.content)]
            break
        except:
            await nepbot.reply(_getError())

    while(True):
        await nepbot.reply("Is the Pokemon Shiny?")
        msg = await nepbot.wait_for_message(author=message.author)
        if msg.content.lower() in ['y', "yes"]:
            cr -= 10
            break
        elif msg.content.lower() in ['n', "no"]:
            break
        else:
            await nepbot.reply(_getError())
            
    while(True):
        await nepbot.reply("Is the Pokemon Legendary?")
        msg = await nepbot.wait_for_message(author=message.author)
        if msg.content.lower() in ['y', "yes"]:
            cr -= 30
            break
        elif msg.content.lower() in ['n', "no"]:
            break
        else:
            await nepbot.reply(_getError())

    while(True):
        await nepbot.reply("How many Persistant Status Afflictions (including Stuck) does the Pokemon have?")
        msg = await nepbot.wait_for_message(author=message.author)
        try:
            cr+= 10* int(msg.content)
            break
        except:
            await nepbot.reply(_getError())
        
    while(True):
        await nepbot.reply("How many Injuries or Volatile Status Afflictions (including Trapped) does the Pokemon have?")
        msg = await nepbot.wait_for_message(author=message.author)
        try:
            cr+= 5* int(msg.content)
            break
        except:
            await nepbot.reply(_getError())

    while(True):
        await nepbot.reply("Did you crit the Accuracy Check?")
        msg = await nepbot.wait_for_message(author=message.author)
        if msg.content.lower() in ['y', "yes"]:
            cr += 10
            break
        elif msg.content.lower() in ['n', "no"]:
            break
        else:
            await nepbot.reply(_getError())

    while(True):
        await nepbot.reply("Enter any other Bonuses as a positive number")
        msg = await nepbot.wait_for_message(author=message.author)
        try:
            cr += int(msg.content)
            break
        except:
            await nepbot.reply(_getError())

    await nepbot.reply("The Capture Rate is `{}`!".format(cr))
    res = dice.roll(100).result
    success = res == 100 or res <= cr
    result  = "succeeded!" if success else "failed..."
    await nepbot.reply("You {} `({})`".format(result, res))
    
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
    try:
        page = requests.get('http://xkcd.com/{}'.format(number))
        tree = html.fromstring(page.content)
        
        comic = tree.xpath('//div[@id="comic"]/img/attribute::src')[0]
        hover = tree.xpath('//div[@id="comic"]/img/attribute::title')[0]
        comic = requests.get("http:{}".format(comic)).content
        
        await nepbot.upload(io.BytesIO(comic), "xkcd-{}.png".format(number))
        await nepbot.say("_{}_".format(hover))
    except Exception as e:
        print(e)
        await nepbot.say("I failed...")

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

nepbot.run(email, passw)
