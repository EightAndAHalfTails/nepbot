import discord
from discord.ext import commands
import cah
from credentials import tokens
import os

desc = "I-It's not like I want to play Cards Against Humanity with you or anything!"

noirebot = commands.Bot(command_prefix=commands.when_mentioned, description=desc)

games = {}
root = os.path.dirname(os.path.realpath(__file__))
save_path = os.path.join(root, "./cah/states")

@noirebot.event
async def on_ready():
    print('Logged in as')
    print(noirebot.user.name)
    print(noirebot.user.id)
    print('------')
    for server in noirebot.servers:
        games[server] = cah.Game()
        filename = os.path.join(save_path, server.name)
        if os.path.isfile(filename):
            games[server] = games[server].load(filename)
        
@noirebot.event
async def on_server_join(server):
    games[server] = cah.Game()

@noirebot.event
async def on_server_remove(server):
    del games[server]

@noirebot.event
async def on_message(message):
    if message.server in games:
        if games[message.server]:
            filename = os.path.join(save_path, message.server.name)
            games[message.server].save(filename)
    await noirebot.process_commands(message)

def _getError():
    return choice(["What?", "Wait, what?", "That doesn't make any sense!", "Huh?", "Could you please repeat that?", "What's that supposed to mean?", "That can't be right...", "Uhhh, what?", "A-Are you okay?", "Hmm?" ])

@noirebot.command(aliases=["join"], help="Accepts an invite to a Discord server.")
async def accept(invite_url:str):
    try:
        await noirebot.accept_invite(invite_url)
        await noirebot.reply("Thanks!")
    except Exception as e:
        await noirebot.reply("It didn't work...")
        await noirebot.say("({})".format(e))

@noirebot.command(pass_context=True, help="leaves a server.")
async def leave(ctx):
    await noirebot.say("Goodbye!")
    await noirebot.leave_server(ctx.message.server)

@noirebot.command(pass_context=True,help="Joins a game in progress.")
async def letmein(ctx):
    games[ctx.message.server].add_player(ctx.message.author)
    await noirebot.reply("Okay, I've added you to the game.")

@noirebot.command(pass_context=True,help="Leaves a game in progress.")
async def letmeout(ctx):
    games[ctx.message.server].remove_player(ctx.message.author)
    await noirebot.reply("Okay, I've removed you from the game.")

@noirebot.command(pass_context=True,help="Resets the current game.")
async def reset(ctx):
    if ctx.message.server in games:
        if games[ctx.message.server]:
            games[ctx.message.server].reset()
            await noirebot.say("Okay, The game has been reset.")
            return
    games[ctx.message.server] = cah.Game()

@noirebot.command(pass_context=True,help="Gives details of the current game.")
async def status(ctx):
    stat = games[ctx.message.server].status()
    await noirebot.say("```{}```".format(stat))

@noirebot.command(pass_context=True,help="PMs you your view of the game.")
async def view(ctx):
    stat = games[ctx.message.server].players[ctx.message.author].status()
    await noirebot.whisper("```{}```".format(stat))

@noirebot.command(pass_context=True,help="Plays the nth card in your hand.")
async def play(ctx, n):
    try:
        num = int(n)
    except:
        pass
    games[ctx.message.server].players[ctx.message.author].play(num)
    await noirebot.say("```{}```".format(games[ctx.message.server].status()))

@noirebot.command(pass_context=True,help="Takes back the cards you have played so far.")
async def clear(ctx):
    games[ctx.message.server].players[ctx.message.author].clear()

@noirebot.command(pass_context=True,help="Votes for a winner.")
async def vote(ctx, name):
    for member in ctx.message.mentions:
        if member != noirebot.user:
            if member in games[ctx.message.server].players:
                games[ctx.message.server].players[ctx.message.author].vote(games[ctx.message.server].players[member])
                await noirebot.say("Congratulations, {0.mention}!".format(member))
                await noirebot.say("```{}```".format(games[ctx.message.server].status()))
                return
            else:
                await noirebot.reply("That person isn't playing.")
    await noirebot.reply("I don't know that person.")

@noirebot.command(pass_context=True,help="Assigns a player to be Card Tsar.")
async def appoint(ctx, name):
    for member in ctx.message.mentions:
        if member != noirebot.user:
            if member in games[ctx.message.server].players:
                games[ctx.message.server].choose_tsar(games[ctx.message.server].players[member])
                await noirebot.say("{0.mention} is the Card Tsar.".format(member))
                return
            else:
                await noirebot.reply("That person isn't playing.")
    await noirebot.reply("I don't know that person.")

noirebot.run(tokens["noire"])
