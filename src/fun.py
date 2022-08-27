from json import loads
from urllib import request
from urllib.error import URLError, HTTPError
from discord.ext import commands
from random import choice
from random import randint
from configs import custom
from configs import settings
from src import logbook


class Fun(commands.Cog):
    __slots__ = ["client", "log"]

    def __init__(self, client):
        self.client = client
        self.log = logbook.getLogger(self.__class__.__name__)


    # ═══ Commands ═════════════════════════════════════════════════════════════════════════════════════════════════════
    @commands.command(aliases=["coin", "toss"])
    async def flip(self, message):
        coin = ["heads", "tails"]
        return await message.send("It's {}!".format(choice(coin)))


    @commands.command(aliases=["dice", "roll", "r"])
    async def rng(self, message, *, numbers: str = None):
        """ Rolls a number ranging from 1 to `numbers`. Rolls as many times as integers within `numbers`.
        Max amount of rolls is 20. Can also be shortened to a multiplication like `20x5`. """
        if numbers is None:
            return await message.send("You can roll the dice for example with `" + custom.PREFIX[0] + " roll 20` or several times with `" + custom.PREFIX[0] + " roll 20 x5` or `" + custom.PREFIX[0] + " roll 20 20 20`")

        numbers_list = list(numbers.split(" "))
        roll_list = []

        # Single roll or mushed together multiple rolls
        if len(numbers_list) == 1:
            if (numbers.find("x") >= 1):
                try:
                    multiplicand = int(numbers[:numbers.find("x")])
                    multiplier = int(numbers[numbers.find("x") + 1:])

                    if (multiplier > 20):
                        return await message.send("Let's keep it reasonable.")
                    elif (multiplicand < 1) or (multiplier < 1):
                        raise ValueError

                    while (multiplier > 0):
                        try:
                            roll_list.append(randint(1, multiplicand))
                            multiplier -= 1
                        except (TypeError, ValueError):
                            return await message.send("I need a positive number to roll. :eyes:")

                    rolled_str = ""
                    for rolled_num in roll_list:
                        rolled_str += "`" + str(rolled_num) + "` "
                    return await message.send("{} rolled {}".format(message.author.display_name, rolled_str) + ".")

                except (TypeError, ValueError):
                    return await message.send("I need a positive number to roll. :eyes:")
            
            elif (numbers.find("*") >= 1):
                try:
                    multiplicand = int(numbers[:numbers.find("*")])
                    multiplier = int(numbers[numbers.find("*") + 1:])

                    if (multiplier > 20):
                        return await message.send("Let's keep it reasonable.")
                    elif (multiplicand < 1) or (multiplier < 1):
                        raise ValueError

                    while (multiplier > 0):
                        try:
                            roll_list.append(randint(1, multiplicand))
                            multiplier -= 1
                        except (TypeError, ValueError):
                            return await message.send("I need a positive number to roll. :eyes:")
                    
                    rolled_str = ""
                    for rolled_num in roll_list:
                        rolled_str += "`" + str(rolled_num) + "` "
                    return await message.send("{} rolled {}".format(message.author.display_name, rolled_str) + ".")

                except (TypeError, ValueError):
                    return await message.send("I need a positive number to roll. :eyes:")

            else:
                try:
                    number = int(numbers_list[0])
                    return await message.send("{} rolled `{}`.".format(message.author.display_name, randint(1, number)))
                except (TypeError, ValueError):
                    return await message.send("I need a positive number to roll. :eyes:")

        # Check for multiplicator
        multiplicator = 0
        if (len(numbers_list) == 2) and (numbers_list[1].startswith(("x", "*"))):
            try:
                multiplicator = int(numbers_list[1][1:])
                if multiplicator < 1:
                    raise ValueError
            except (TypeError, ValueError):
                return await message.send("I need a positive number to roll. :eyes:")

        elif (len(numbers_list) == 3) and ((numbers_list[1] == "x") or (numbers_list[1] == "*")):
            try:
                multiplicator = int(numbers_list[2])
                if multiplicator < 1:
                    raise ValueError
            except (TypeError, ValueError):
                return await message.send("I need a positive number to roll. :eyes:")

        # Roll <multiplicator> times
        if multiplicator > 0:
            if multiplicator > 20:
                return await message.send("Let's keep it reasonable.")
            while (multiplicator > 0):
                try:
                    number = int(numbers_list[0])
                    roll_list.append(randint(1, number))
                    multiplicator -= 1
                except (TypeError, ValueError):
                    return await message.send("I need a positive number to roll. :eyes:")
            
            rolled_str = ""
            for rolled_num in roll_list:
                rolled_str += "`" + str(rolled_num) + "` "
            return await message.send("{} rolled {}".format(message.author.display_name, rolled_str) + ".")
        
        # Roll all specific rolls
        else:
            false_input_count = 0
            for number in numbers_list:
                try:
                    number = int(number)
                    roll_list.append(randint(1, number))
                except (TypeError, ValueError):
                    false_input_count += 1
            
            if false_input_count == len(numbers_list):
                return await message.send("I need a positive number to roll. :eyes:")

            rolled_str = ""
            for rolled_num in roll_list:
                rolled_str += "`" + str(rolled_num) + "` "
            
            return await message.send("{} rolled {}".format(message.author.display_name, rolled_str) + ".")


    @commands.command(aliases=custom.QUESTION_TRIGGER)
    async def eightball(self, message, *, question:str = None):
        """ Maon replies with a variation of yes / no / maybe to the eightball command or aliases specified
        in the config file. Default settings simulate an answer to a closed question. """  
        if question is None:
            return await message.send(choice(custom.DEFAULT_REPLY))
        else:
            if "why" in message.invoked_with:
                return await message.send(choice(custom.QUESTION_REPLY_WHY))
            return await message.send(choice(custom.QUESTION_REPLY))


    @commands.command(aliases=["anime", "animu", "hentai", "manga"])
    async def mal(self, message, *args: str):
        """ Looks up an anime or manga title on MyAnimeList specified by search terms in `args`. """
        if not args:
            return await message.send(
                "You can search for an anime if you provide me a search term. I'll look for the closest one I can find `" + custom.PREFIX[0] + "anime <key words>`")
        
        query = "%20".join(args)
        for char in query:
            if settings.RFC_3986_CHARS.find(char) < 0:
                query = query.replace(char, "")
        
        if len(query) < 3:
            return await message.send("Search terms have to be at least 3 characters.")
        elif len(query) > 150:
            query = query[:150]
        
        try:
            if "manga" in message.invoked_with:
                resp = request.urlopen(request.Request(settings.MAL_API_MANGA_SEARCH_URL + query))
            else:
                resp = request.urlopen(request.Request(settings.MAL_API_ANIME_SEARCH_URL + query))
            data = loads(resp.read().decode("utf-8"))
            first_entry = data.get("results")[0]
            return await message.send(first_entry.get("url"))

        except (URLError, HTTPError):
            return await message.send("I could not fetch any information, maybe try again in a few seconds.")


    @commands.command(aliases=["umfrage"])
    async def poll(self, message, *args: str):
        if len(args) <= 0:
            await message.send(f"You can create a simple yes / no poll with  `{custom.PREFIX[0]}poll Do you like cats?`\n\nOr you can create a poll with multiple choices like this\n`{custom.PREFIX[0]}poll Your favorite ice cream flavor is... -o banana -o strawberry -o chocolate`")
            poll_message = await message.send(f"And it will look like this:\n:mega:  **Your favorite ice cream flavor is...**\n\n:one:  banana\n:two:  strawberry\n:three:  chocolate")
            return await self.load_poll_choice_selectors(poll_message, 3)

        poll_string = " ".join(args)
        if len(poll_string) >= 500:
            return await message.send("Try to keep the length of the poll reasonable.")

        if poll_string.find("-o") < 0:
            poll_selectors = [
                "\N{WHITE HEAVY CHECK MARK}",
                "\N{REGIONAL INDICATOR SYMBOL LETTER X}"
            ]
            poll_message = await message.send(f":mega:  **{poll_string}**")
            for i in range(2):
                await poll_message.add_reaction(poll_selectors[i])

        else:
            # trim the poll headline question
            poll_headline = poll_string[:poll_string.find("-o")].rstrip()
            poll_string = poll_string[poll_string.find("-o") + 2:].lstrip()
            poll_options = []
            i = 0
            n = poll_string.count("-o")
            while i <= n:
                poll_choice = poll_string[:poll_string.find("-o") if poll_string.find("-o") + 1 else len(poll_string)]
                if not (len(poll_choice.strip()) <= 0):
                    poll_options.append(poll_choice)
                if not poll_string.find("-o") < 0:
                    poll_string = poll_string[poll_string.find("-o") + 2:].lstrip()
                i += 1

            if len(poll_options) > 10:
                return await message.send("I can't display so many choices...")

            poll_choice_emojis = [
                ":one:", ":two:", ":three:", ":four:", ":five:", ":six:",
                ":seven:", ":eight:", ":nine:", ":keycap_ten:" 
            ]
            i = 0
            poll_message_content = ""
            if poll_headline:
                poll_message_content += f"**:mega:  {poll_headline}**\n\n"
            for choice in poll_options:
                poll_message_content += f"{poll_choice_emojis[i]}  {choice}\n"
                i += 1
            
            poll_message = await message.send(poll_message_content)
            return await self.load_poll_choice_selectors(poll_message, len(poll_options))


    async def load_poll_choice_selectors(self, message, n: int):
        poll_selectors = [
            "\u0031\u20E3",
            "\u0032\u20E3",
            "\u0033\u20E3",
            "\u0034\u20E3",
            "\u0035\u20E3",
            "\u0036\u20E3",
            "\u0037\u20E3",
            "\u0038\u20E3",
            "\u0039\u20E3",
            "\N{KEYCAP TEN}"
        ]
        for i in range(n):
            await message.add_reaction(poll_selectors[i])


    # ═══ Events ═══════════════════════════════════════════════════════════════════════════════════════════════════════
    @commands.Cog.listener()
    async def on_message(self, message):
        """ Maon replies with a variation of "what?" if only her prefix is called without any command. """ 
        if message.author.id != self.client.user.id:
            if message.content.lower() == custom.PREFIX_FAST:
                return await message.channel.send(choice(custom.DEFAULT_REPLY))


# ═══ Cog Setup ════════════════════════════════════════════════════════════════════════════════════════════════════════
async def setup(maon: commands.Bot):
    await maon.add_cog(Fun(maon))


async def teardown(maon: commands.Bot):
    await maon.remove_cog(Fun)
