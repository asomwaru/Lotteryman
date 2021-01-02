import random
import json

import asyncio
import discord
from discord.ext import commands
from pymongo import MongoClient

bot = commands.Bot(command_prefix="*", description="A bot", case_insensitive=True)

configs = {}
with open("config.json", "r") as fh:
    configs = json.load(fh)

client = MongoClient(f"{configs['login_string']}")
mudae = client["mudaeDB"]


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
    roles = list(map(str, ctx.message.author.roles))

    if any([x for x in roles if x in configs['valid_roles']]):  # any([x for x in roles if x in config['valid_roles']])
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
    people.set_image(
        url="https://cdn.discordapp.com/avatars/788119348040171543/51160a680f2e1106b5510b7379f467a4.png?size=1024")

    for x in users:
        people.add_field(name=f"{str(x)}", value="ㅤ", inline=True)

    await ctx.send(embed=people)

    winner = random.choice(users)

    await ctx.send(f"The winner of the lottery is {winner.mention}")


@bot.command(aliases=["char", "c", "ch"])
async def character(ctx, *message):
    name = " ".join(message).strip()

    character = mudae.characters.find_one({"name": name})

    if character is None:
        name = " ".join(message).strip()

        if '(' in name:
            name = ' '.join(message[:-1])
        else:
            name = ' '.join(message[:])

        for x in mudae.characters.find({"name": {"$regex": f"^{name}", "$options": 'i'}}):
            name = " ".join(message).lower()

            if name == x['name'].lower():
                character = x
                break
        else:
            await ctx.send("Cannot find character :(")
            return

    r = lambda: random.randint(0, 255)
    color = '%02X%02X%02X' % (r(), r(), r())
    person = discord.Embed(title=f"{character['name']}", color=int(color, 16))

    person.add_field(name="Series", value=f"*{character['series']}*", inline=False)
    person.add_field(name="Rank 👑", value=f"#{character['rank']}", inline=True)
    person.add_field(name="Kakera<:kakeraR:780263031203823658>", value=f"{character['kakera']}ka", inline=True)

    person.set_image(url=f"{character['image']}")
    person.set_footer(text=character['owner'])

    await ctx.send(embed=person)


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
bot.run(configs["login_token"])
