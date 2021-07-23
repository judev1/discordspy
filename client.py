import time
import asyncio
from collections import deque

import discord
import aiohttp
from aiohttp import web
from discord.ext import tasks

from . import utils
#import utils

class Client:
    """ The client class used to interact with the Discords.com API """

    def __init__(self, bot: discord.Client, token: str,
                 post: utils.PostObject = None):
        """ Sets up and returns a discordspy Client object

                -- ARGUMENTS --

            :bot: is a discord Client

            :token: is your Discords.com api token

            :post: is a PostObject used to determine how the client will handle
            server count posting
        """

        self.bot = bot
        self.token = token

        self.endpoint = utils.Ratelimit(5, 10)
        self.queue = deque(maxlen=1)
        self.has_webhook = False

        if not post:
            return

        if post.auto:

            async def on_server_change(server):
                await self.post_servers()

            self.bot.add_listener(on_server_change, "on_guild_join")
            self.bot.add_listener(on_server_change, "on_guild_remove")

        elif post.intervals:

            loop = tasks.loop(seconds=post.interval)
            loop(self.post_servers).start()

    def servers(self):
        return len(self.bot.guilds)
    guilds = servers

    async def post_servers(self):
        """ A method to post the server count to the Discords.com API """

        if not self.bot.is_ready():
            return

        timestamp = time.time()
        self.queue.append(timestamp)

        if self.endpoint.is_ratelimited():
            await asyncio.sleep(self.endpoint.until_reset())

        if timestamp not in self.queue:
            return

        url = f"https://discords.com/bots/api/bot/{self.bot.user.id}"
        headers = {"Authorization": self.token}
        data = {"server_count": self.servers()}

        self.endpoint.emulate()

        session = aiohttp.ClientSession()
        async with session.post(url, headers=headers, data=data) as res:
            self.bot.dispatch("discords_server_post", res.status)
            self.bot.dispatch("discords_guild_post", res.status)
        await session.close()

    post_guilds = post_servers

    def webhook(self, port: int = None, auth: str = "", path: str = "/discordswebhook"):
        """ A method to recieve voting webhooks from Discords.com

                -- ARGUMENTS --

            :port: is the port that will be used to listen to webhook requests

            :auth: is the optional auth used to verify that the webhook is
            coming from Discords.com
        """

        if self.has_webhook:
            return

        async def on_post_request(request):

            print("Recieved a request")

            headers = request.headers
            if headers.get("Authorization") != auth:
                return web.Response(status=401)

            try: data = await request.json()
            except: return web.Response(status=400)

            if data.get("type") == "vote":
                self.bot.dispatch("discords_vote", data)
            elif data.get("type") == "test":
                self.bot.dispatch("discords_test", data)
            return web.Response(status=200)

        async def start():

            app = web.Application(loop=self.bot.loop)
            app.router.add_post(path, on_post_request)

            runner = web.AppRunner(app)
            await runner.setup()

            server = web.TCPSite(runner, "0.0.0.0", port)
            await server.start()

        self.bot.loop.create_task(start())
        self.has_webhook = True