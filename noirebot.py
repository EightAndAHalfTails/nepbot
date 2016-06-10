import discord
from discord.ext import commands
import cah
from credentials import noire

desc = "I-It's not like I want to play Cards Against Humanity with you or anything!"

noirebot = commands.Bot(command_prefix=commands.when_mentioned, description=desc)

games = {}

@noirebot.event
async def on_ready():
    print('Logged in as')
    print(noirebot.user.name)
    print(noirebot.user.id)
    print('------')

@noirebot.event
async def on_server_join(server):
    games[server] = Game(noirebot)

@noirebot.event
async def on_server_remove(server):
    del games[server]

def _getError():
    return choice(["What?", "Wait, what?", "That doesn't make any sense!", "Huh?", "Could you please repeat that?", "What's that supposed to mean?", "That can't be right...", "Uhhh, what?", "A-Are you okay?", "Hmm?" ])

@noirebot.command(aliases=["join"], help="Accepts an invite to a Discord server.")
async def accept(invite_url:str):
    try:
        await noirebot.accept_invite(invite_url)
        await noirebot.reply("Thanks!")
    except:
        await noirebot.reply("It didn't work...")

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
    games[ctx.message.server].reset()
    await noirebot.say("Okay, The game has been reset.")

@noirebot.command(pass_context=True,help="Gives details of the current game.")
async def status(ctx):
    stat = games[ctx.message.server].status()
    await noirebot.say("```{}```".format(stat))

@noirebot.command(pass_context=True,help="PMs you your view of the game.")
async def view(ctx):
    stat = games[ctx.message.server].player[ctx.message.author].status()
    await noirebot.whisper("```{}```".format(stat))

@noirebot.command(pass_context=True,help="Plays the nth card in your hand.")
async def play(ctx, n):
    games[ctx.message.server].player[ctx.message.author].play(n)

@noirebot.command(pass_context=True,help="Takes back the cards you have played so far.")
async def clear(ctx):
    games[ctx.message.server].player[ctx.message.author].clear()

@noirebot.command(pass_context=True,help="Votes for a winner.")
async def vote(ctx, name):
    for member in ctx.message.server.members:
        if member.mentioned_in(ctx.message):
            if member in games[ctx.message.server].players:
                games[ctx.message.server].player[ctx.message.author].vote(member)
                return
            else:
                noirebot.reply("That person isn't playing.")
    noirebot.reply("I don't know that person.")

noirebot.run(noire.email, noire.passw)
