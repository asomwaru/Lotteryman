import asyncio
import json
import random
from pprint import pprint

import discord
import pymongo
from discord.ext import commands
from pymongo import MongoClient

bot = commands.Bot(command_prefix=":", description="A bot", case_insensitive=True)

configs = {}
with open("config.json", "r") as fh:
    configs = json.load(fh)

wishes = {}
with open("wishes.json", "r") as fh:
    wishes = json.load(fh)

client = MongoClient(f"{configs['login_string']}")
mudae = client["mudaeDB"]


def rand_col():
    r = lambda: random.randint(0, 255)
    color = '%02X%02X%02X' % (r(), r(), r())

    return color


@bot.event
async def on_error(event, *args, **kwargs):
    pass


@bot.event
async def on_ready():
    print("Good day!")
    await bot.change_presence(status=None, activity=discord.CustomActivity(name="My prefix is :"))


# @bot.event
# async def on_message(message):
# words = message.content.lower().split()
# if any(["$wish" in x for x in words]):
#     character = " ".join(words[1:])
#     print(character)
#     pprint(words)
#     print(str(message.author))
#     print()
#
#     owner = str(message.author)
#
#     await asyncio.sleep(2)
#
#     if any([x for x in message.reactions if x.emoji == "✅"]):
#         return
#
#     if len([x for x in wishes[owner] if character == x]) >= 1:
#         return
#
#     wishes[owner].append(character)


@bot.event
async def on_raw_reaction_remove(payload):
    channel = bot.get_channel(payload.channel_id)
    msg = await channel.fetch_message(payload.message_id)

    if msg.author.name != configs['bot_info']['name']:
        return

    embed = msg.embeds[0]

    owner = None
    series = None

    field = embed.fields[0]

    if "Harem" in field.name.split():
        owner = field.name.split()[:-1]
        owner = " ".join(owner)[:-2]

        field = field.value.split('\n')[-1]
        field = field.split()
        last_char = " ".join(field[1:-1])
    else:
        series = field.name

        field = field.value.split('\n')[-1]
        field = field.split()

        dash = field.index('-')
        last_char = " ".join(field[1:dash])

    if owner:
        owned = [x['name'] for x in mudae.characters.find({"owner": owner}).sort('rank', pymongo.ASCENDING)]
        index = owned.index(last_char) // 15
    else:
        owned = [x['name'] for x in mudae.characters.find({"series": series}).sort('rank', pymongo.ASCENDING)]
        index = owned.index(last_char) // 15

    if payload.emoji.name in ["⬅", '⬅️']:
        current = (index - 1) * 15
        if current < 0:
            return

    elif payload.emoji.name in ["➡", '➡️']:
        current = (index + 1) * 15

    else:
        print("Invalid emoji")
        return

    embed.remove_field(0)

    string = ""
    if owner:
        characters = list(
            mudae.characters.find({"owner": owner}, limit=15, skip=current).sort('rank', pymongo.ASCENDING))

        for y in characters:
            string += f"#**{y['rank']}**: {y['name']} **{y['kakera']}**ka\n"

        embed.add_field(name=f"{owner}'s Harem", value=string, inline=True)
        embed.set_footer(text=owner)

    else:
        characters = list(
            mudae.characters.find({"series": series}, limit=15, skip=current).sort('rank', pymongo.ASCENDING))

        for y in characters:
            string += f"#**{y['rank']}**: {y['name']} - {y['owner']}\n"

        embed.add_field(name=f"{series}", value=string, inline=True)

    url = characters[0]['image']
    embed.set_thumbnail(url=url)

    await msg.edit(embed=embed)


@bot.event
async def on_reaction_add(reaction, user):
    if reaction.message.author.name != configs['bot_info']['name']:
        return
    elif user.name == configs['bot_info']['name']:
        return

    msg = reaction.message
    embed = msg.embeds[0]

    if len(embed.fields) > 1:
        return

    owner = None
    series = None

    field = embed.fields[0]

    if "Harem" in field.name.split():
        owner = field.name.split()[:-1]
        owner = " ".join(owner)[:-2]

        field = field.value.split('\n')[-1]
        field = field.split()
        last_char = " ".join(field[1:-1])
    else:
        series = field.name

        field = field.value.split('\n')[-1]
        field = field.split()

        dash = field.index('-')
        last_char = " ".join(field[1:dash])

    if owner:
        owned = [x['name'] for x in mudae.characters.find({"owner": owner}).sort('rank', pymongo.ASCENDING)]
        index = owned.index(last_char) // 15
    else:
        owned = [x['name'] for x in mudae.characters.find({"series": series}).sort('rank', pymongo.ASCENDING)]
        index = owned.index(last_char) // 15

    if reaction.emoji == "⬅":
        current = (index - 1) * 15
        if current < 0:
            return

    elif reaction.emoji == '➡':
        current = (index + 1) * 15

    else:
        return

    embed.remove_field(0)

    string = ""

    if owner:
        characters = list(
            mudae.characters.find({"owner": owner}, limit=15, skip=current).sort('rank', pymongo.ASCENDING))

        for y in characters:
            string += f"#**{y['rank']}**: {y['name']} **{y['kakera']}**ka\n"

        embed.add_field(name=f"{owner}'s Harem", value=string, inline=True)
        embed.set_footer(text=owner)

    else:
        characters = list(
            mudae.characters.find({"series": series}, limit=15, skip=current).sort('rank', pymongo.ASCENDING))

        for y in characters:
            string += f"#**{y['rank']}**: {y['name']} - {y['owner']}\n"

        embed.add_field(name=f"{series}", value=string, inline=True)

    url = characters[0]['image']
    embed.set_thumbnail(url=url)

    await msg.edit(embed=embed)


@bot.command(aliases=["owns", "owned", "o", "mmrk"])
async def owner(ctx, *message):
    id = None

    try:
        id = int("".join(message))
    except ValueError:
        pass

    if len(message) == 1 and id is not None:
        g = ctx.message.channel.guild
        members = g.fetch_members()
        people = [m async for m in members if not m.bot]

        people = [x for x in people if x.id == id]

        if len(people) < 1:
            await ctx.send("Person not found :(")

        owner = str(people[0])

    elif len(message) == 1 and "<" in message[0]:
        g = ctx.message.channel.guild
        members = g.fetch_members()
        people = [m async for m in members if not m.bot]

        id = message[0]
        id = int(id[3:-1])

        people = [x for x in people if x.id == id]

        if len(people) < 1:
            await ctx.send("Person not found :(")

        owner = str(people[0])

    elif len(message) == 0:
        owner = str(ctx.message.author)

        if owner == "¯\_(ツ)_/¯#4793":
            owner = "¯\\_(ツ)_/¯#4793"

        elif len(list(mudae.characters.find_one({"owner": {"$regex": f"^{owner}", "$options": 'i'}}))) < 1:
            await ctx.send("Owner not found")
            return

    elif len(message) >= 1:
        message = " ".join(message).lower()

        owners = mudae.get_collection(name="characters").distinct("owner")

        person_found = [x for x in owners if message in x.lower()]

        if len(person_found) <= 0:
            await ctx.send("No owner found :(")
            return

        elif len(person_found) > 1:
            await ctx.send("Multiple occurences of people. Please specify more.")
            return

        owner = person_found[0]

    else:
        return

    person = discord.Embed(color=int(rand_col(), 16))

    string = "\n"
    for y in mudae.characters.find({"owner": owner}, limit=15).sort('rank', pymongo.ASCENDING):
        string += f"#**{y['rank']}**: {y['name']} **{y['kakera']}**ka\n"

    person.add_field(name=f"{owner}'s Harem", value=string, inline=True)

    person.set_footer(text=owner)

    url = list(mudae.characters.find({"owner": owner}, limit=1).sort('rank', pymongo.ASCENDING))[0]['image']
    person.set_thumbnail(url=url)

    msg = await ctx.send(embed=person)
    await msg.add_reaction(emoji='⬅')
    await msg.add_reaction(emoji='➡')


@bot.command(aliases=["s"])
async def series(ctx, *message):
    series = " ".join(message).lower()

    person = discord.Embed(color=int(rand_col(), 16))
    available_series = list(mudae.characters.distinct("series"))

    if not any([series == x.lower() for x in available_series]):
        await ctx.send("Series not found :(")
        return
    else:
        series = [x for x in available_series if x.lower() == series][0]

    string = "\n"
    for y in mudae.characters.find({"series": series}, limit=15).sort('rank', pymongo.ASCENDING):
        string += f"#**{y['rank']}**: {y['name']} - {y['owner']}\n"

    person.add_field(name=f"{series}", value=string, inline=True)

    url = list(mudae.characters.find({"series": series}, limit=1).sort('rank', pymongo.ASCENDING))[0]['image']
    person.set_thumbnail(url=url)

    msg = await ctx.send(embed=person)
    await msg.add_reaction(emoji='⬅')
    await msg.add_reaction(emoji='➡')


@bot.command(aliases=["char", "c", "ch", "im"])
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

    num = character['rank']
    if num >= 1000:
        thousand = str(num)[:-3]
        hundred = str(num)[-3:]

        num = f"{thousand},{hundred}"
    else:
        num = str(num)

    person.add_field(name="Rank 👑", value=f"#{num}", inline=True)

    num = character['kakera']
    if num >= 1000:
        thousand = str(num)[:-3]
        hundred = str(num)[-3:]

        num = f"{thousand},{hundred}"
    else:
        num = str(num)

    person.add_field(name="Kakera<:kakeraR:780263031203823658>", value=f"{num}ka", inline=True)

    person.set_image(url=f"{character['image']}")
    person.set_footer(text=character['owner'])

    await ctx.send(embed=person)


@bot.command(aliases=["p"])
async def people(ctx):
    people = discord.Embed(color=int(rand_col(), 16))

    string = ""
    for x in mudae.get_collection(name="characters").distinct("owner"):
        string += f"*{x}*\n"

    people.add_field(name=f"Available Users", value=string, inline=True)

    await ctx.send(embed=people)

    await asyncio.sleep(2)


@bot.command(aliases=["sr", "ts"])
async def server_rank(ctx):
    people = discord.Embed(color=int(rand_col(), 16))

    owners = []
    for i, x in enumerate(mudae.get_collection(name="characters").distinct("owner")):
        characters = [x['rank'] for x in mudae.characters.find({"owner": x}, limit=15).sort('rank', pymongo.ASCENDING)]
        owners.append([x, sum(characters)])

    owners = list(sorted(owners, key=lambda x: x[1]))

    string = ""
    for i, x in enumerate(owners):
        string += f"**{i + 1}**: *{x[0]}* - **{x[1]}**\n"

    people.add_field(name=f"User Ranks", value=string, inline=True)

    await ctx.send(embed=people)

    await asyncio.sleep(2)


@bot.command()
async def react(ctx):
    roles = list(map(str, ctx.message.author.roles))

    if len(list(filter(lambda x: x in configs['valid_roles'], roles))) <= 0:
        await ctx.send("You are not a valid user!")
        return

    embed = discord.Embed(title="React to me to partake in the lottery", description="", color=0x00bb7f)

    msg = await ctx.send(embed=embed)

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


@bot.command(aliases=['fu', 'fyip'])
async def lot_ping(ctx, *message):
    roles = list(map(str, ctx.message.author.roles))
    if len(list(filter(lambda x: x in configs['valid_roles'], roles))) <= 0:
        await ctx.send("You are not a valid user!")
        return

    g = ctx.message.channel.guild
    members = g.fetch_members()
    people = [m async for m in members if not m.bot]

    person = random.choice(people)

    if len(message) == 1 and 'all' in message and str(ctx.message.author) == "Walrushman#7410":
        for person in people:
            num = random.randint(1, 10)
            for t in range(1, num + 1):
                await ctx.send(f"{person.mention} has been @'d {t} time(s)")

        return

    pings = random.randint(1, 20)

    if pings == 1:
        await ctx.send(f"{person.mention} prepare for {str(pings)} more @.")
    else:
        await ctx.send(f"{person.mention} prepare for {str(pings)} more @'s.")

    for people in range(1, pings + 1):
        await ctx.send(f"{person.mention} {str(people)}")


@bot.command()
async def destroy(ctx):
    roles = list(map(str, ctx.message.author.roles))
    if len(list(filter(lambda x: x in configs['valid_roles'], roles))) <= 0:
        await ctx.send("You are not a valid user!")
        return
    else:
        await ctx.send("Goodbye")
        await bot.logout()


bot.run(configs["login_token"])
