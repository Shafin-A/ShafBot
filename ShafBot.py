import discord
import pickle
import json
from discord.ext import commands
import shlex
from string import ascii_lowercase
import emoji as emoji_lib
import random

default_poll_emojis = []
for c in ascii_lowercase:
    if c == 'u': # 20 letters
        break
    default_poll_emojis.append(":regional_indicator_" + c + ":")


bot = commands.Bot(command_prefix = '=')

class Shaf_Message:
    def __init__(self, message):
        self.guild_id = message.guild.id
        self.channel_name = message.channel.name
        self.jump_url = message.jump_url

@bot.event
async def on_ready():
    #print(f'{bot.user.name} has connected to Discord!')
    game = discord.Game('=help')
    await bot.change_presence(activity=game)

@bot.command(help="Give a hug to someone!")
async def hug(ctx, user : discord.User):
    with open('hugs.json', 'r') as f:
        hugs_data = json.load(f)

    if str(user.id) in hugs_data:
        hugs_data[str(user.id)] = hugs_data[str(user.id)] + 1
    else:
        hugs_data[str(user.id)] = 1

    with open('hugs.json', 'w') as f:
        json.dump(hugs_data, f)

    await ctx.send("Hugged " + user.mention + "! :hugging:")
    await ctx.send("Awww :smiling_face_with_3_hearts: ")
        
@bot.command(name='displayhug', help="See how many hugs a user has")
async def display_hug(ctx, user : discord.User):
    with open('hugs.json', 'r') as f:
        hugs_data = json.load(f)

    if str(user.id) in hugs_data:
        await ctx.send(user.mention + " has " + str(hugs_data[str(user.id)]) + " hugs :hugging:")
    else:
        await ctx.send(user.mention + " has no hugs... :sob:")
        await ctx.send("Give them a good warm hug! :hugging:")

@bot.command(name='displayhugs', help="See how many hugs each user in the channel has")
async def display_hugs(ctx):
    with open('hugs.json', 'r') as f:
        hugs_data = json.load(f)

    members_in_server = [member.id for member in ctx.guild.members]

    s = ""
    for user_id in sorted(hugs_data.keys(), key=hugs_data.get, reverse=True):
        if int(user_id) in members_in_server:
            s += ctx.guild.get_member(int(user_id)).mention + " - " + str(hugs_data[user_id]) + '\n'

    if not s:
        await ctx.send("Nobody has any hugs in this server... :sob:")
        return

    embed = discord.Embed(title="Hugs on " + ctx.guild.name, description=s, color=0x00ff00)
    await ctx.send(embed=embed)
        
@bot.command(name='lastpoll', help='Gives a link to the last poll')
async def last_poll(ctx):
    with open('polls.data', 'rb') as pickle_file:
        polls = pickle.loads(pickle_file.read())
        if not polls:
                await ctx.send("No polls have been made since bot started")
                return
        for poll in reversed(polls):
            if poll.guild_id == ctx.guild.id:
                if poll.channel_name == ctx.channel.name:
                    await ctx.send("Last poll in '" +  ctx.channel.name + "' was at: " + poll.jump_url)
                    return
        await ctx.send("Could not find any recent polls in '" + ctx.channel.name + "' in history")
        
@bot.command(help=\
             'Ask a poll question.\
\nSyntax 1: \n=poll "poll question" "option 1" "option 2" \
\nSyntax 2: \n=poll\npoll question\noption 1\noption 2 \n\
Add custom poll emojis by adding an emoji before the poll options')
async def poll(ctx):
    #args = ctx.message.content[5:].split() 
    #command = args.pop(0).lower()

    if '\n' in ctx.message.content:
        args = ctx.message.content[1:].split('\n')
    else:
        args = shlex.split(ctx.message.content[1:])
    args.pop(0) # poll command
    poll_question = args.pop(0)

    if (len(args) > 20): # can't have more than 20 reactions
        await ctx.send("Too many args!!!!!!")
        return
    
    poll_question = ":bar_chart: **" + poll_question + "**"
    poll = ""
   # await message.delete(delay=10) # delete the original message, looks nicer ?

    emojis_used = [] # to be used as reactions to the message later
    for i in range(len(args)):
        emoji = args[i].split()[0] #get the first word in the poll option
        try:
            # check if its an emoji by trying to add emoji reaction
            # will throw error to be caught if not an emoji
            await ctx.message.add_reaction(emoji)
            await ctx.message.clear_reaction(emoji)
            emojis_used.append(emoji)
            poll += args[i] + "\n"                
        except:
            # not an emoji, assign a default letter emoji based on current index
            emoji = emoji_lib.emojize(default_poll_emojis[i], use_aliases=True)
            emojis_used.append(emoji)
            poll += emoji + " " + args[i] + "\n"

    embed = discord.Embed(description=poll, color=0x00ff00)
    await ctx.send(poll_question)
    
    # send msg as embed and react with emojis as poll options
    sent_msg = await ctx.send(embed = embed)
    for emoji in emojis_used:
        await sent_msg.add_reaction(emoji)

    with open('polls.data', 'rb') as f:
        polls = pickle.loads(f.read())

    polls.append(Shaf_Message(sent_msg)) # set last poll
    with open('polls.data', 'wb') as f:
        pickle.dump(polls, f)
        
bot.run('API key goes here')
