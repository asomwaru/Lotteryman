import random
import asyncio
import discord
from discord.ext import commands

bot = commands.Bot(command_prefix="*", description="A bot")

@bot.command()
async def hello(ctx):
    await ctx.send("Hello!")

@bot.command()
async def ping(ctx):
    await ctx.send("pong")

@bot.command()
async def say(ctx, *message):
    await ctx.send(" ".join(message))

@bot.command()
async def react(ctx):
    r = list(map(str, ctx.message.author.roles))

    if "Bot Controller" not in r:
        await ctx.send("You are not a valid user!")
        return

    embed = discord.Embed(title="React to me to partake in the lottery", description="", color=0x00bb7f)

    msg = await ctx.send(embed=embed)

    await msg.add_reaction(emoji='R')
    await asyncio.sleep(5)

    msg = await msg.channel.fetch_message(msg.id)

    users = [y for x in msg.reactions async for y in x.users()]
    users = list(set(users))
    users = [x for x in users if str(x) != "Lotteryman#2019"]

    people = discord.Embed(title="Users Reacted: ", color=0x00bb7f)
    people.set_image(url="https://cdn.discordapp.com/avatars/788119348040171543/51160a680f2e1106b5510b7379f467a4.png?size=1024")

    for x in users:
        people.add_field(name=f"{str(x)}", value="ㅤ", inline=True)

    await ctx.send(embed=people)

    freekak = random.choice(users)

    await ctx.send(f"$givek {freekak.mention} 1")
    await asyncio.sleep(1)
    await ctx.send("y")


@bot.command()
async def destroy(ctx):
    r = ctx.message.author.roles

    if "bot dweebs" not in r:
        await ctx.send("You are not a valid user!")
        return
    else:
        await ctx.send("Goodbye")
        await bot.logout()

print("Good day!")
bot.run("Nzg4MTE5MzQ4MDQwMTcxNTQz.X9e3Vw.rPI_h43B12uH4ofSduvVVWbsp04")