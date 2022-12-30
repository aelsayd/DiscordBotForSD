import discord
from discord.ext import commands
from main import generate
from main import evolve as _evolve
import datetime as dt
import os
import openai

token = "[DISCORDTOKEN]"
openai.api_key = "[OPENAIKEY]"

intents = discord.Intents.all()

prefix = '!'
bot = commands.Bot(command_prefix=prefix, intents=intents)


@bot.command()
async def hello(ctx):
    await ctx.send("Hello!")

users = {}
seeds = {}

@bot.command(help="Evolves last image generated. Options: [0,1] for whichever image you wish to evolve")
async def evolve(ctx, message:str="0"):
    #try:
    ix = int(message)
    seed = seeds[ctx.author][ix]
    message = users[ctx.author]
    message = message.replace('/', '\\/')
    split = message.split("||")
    prompt = split[0]
    await ctx.reply("Evolving for " + prompt)

    if(len(split) > 1):
        split = split[1].split["x"]
        width = split[0]
        height = split[1]
        path = await callEvolve(prompt, seed, width, height)
    else: 
        path = await callEvolve(prompt, seed)

    await ctx.reply(file=discord.File(path))
    print(seed)
    #except Exception as e:
    #    await ctx.reply("something went wrong")


@bot.command(name="prompt", help="Uses the message to generate an image")
async def prompt(ctx, *, message:str):
    users[ctx.author] = message
    await ctx.reply("Prompted for " + message)
    await callGen(message, ctx)

@bot.command(name="re", help="retries the last prompt again")
async def re(ctx):
    try:
        message = users[ctx.author]
        await ctx.reply("Prompted for" + message)
        reply = await callGen(message, ctx)
    except:
        await ctx.reply("You dont have any previous registered commands.")


async def callEvolve(message, seed, width=512, height=512):
    fileName = dt.datetime.now().strftime('%Y%m%d%H%M%S')
    path = "playground/public/" + fileName + ".png"
    _evolve(seed, message, path, width, height, rows=1, cols=2)
    return path

async def callGen(message, ctx):
    try:
        message = message.replace('/', '\\/')
        split = message.split("||")
        fileName = dt.datetime.now().strftime('%Y%m%d%H%M%S')
        path = "playground/public/" + fileName + ".png"
        prompt = split[0]
        if(len(split) > 1):
            seed = generate(prompt, 20, path , width=int(split[1].split("x")[0]), height=int(split[1].split("x")[1]), rows=1, columns=2)
        else:
            seed= generate(prompt, 20, path, rows=1, columns=2)
        reply = await ctx.reply(file=discord.File(path))
        seeds[ctx.author] = seed
    except:
        reply = await ctx.reply("Something went wrong with your request. ;-;")

    return reply

@bot.command(name="ask", help="prompts open ai's davinci")
async def callDavinci(ctx, *, message:str):
    print(message)
    
    response = openai.Completion.create(
      model="text-davinci-003",
      prompt=message,
      temperature=0.7,
      max_tokens=512,
      top_p=1,
      frequency_penalty=0,
      presence_penalty=0
    )
    
    await ctx.reply(response["choices"][0]["text"])

bot.run(token)
