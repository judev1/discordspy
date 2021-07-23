# The offical Python API wrapper for Discords.com

### Notices
This is the first version with limited coverage of API endpoints, more features, functionality and documentation will be added in the future.


### Installation:
```
pip install discords.py
```

### Features
 - Server count posting
 - Built-in automatic & interval server count posting
 - Built-in voting and webhook handlers
 - Voting and server posting events

### Examples

#### Automatic server count posting with event
Autoposting posts the servercount whenever a server is joined/removed while abiding with ratelimits
```py
from discord.ext import commands
import discordspy

bot = commands.Bot("!")
discords = discordspy.Client(bot, DISCORDS_TOKEN, post=discordspy.Post.auto())

@bot.event
async def on_discords_server_post(status):
    if status == 200:
        print("Posted the server count:", discords.servers())

bot.run(TOKEN)
```

#### Interval server count posting every hour and a half
```py
from discord.ext import commands
import discordspy

bot = commands.Bot("!")
post = discordspy.Post.interval(minutes=30, hours=1)
discords = discordspy.Client(bot, DISCORDS_TOKEN, post=post)

@bot.event
async def on_discords_server_post(status):
    if status == 200:
        print("Posted the server count:", discords.servers())

bot.run(TOKEN)
```

#### Webhook voting event
IMPORTANT: Your webhook url must end with `/discordswebhook` if you wish to use a different path, please specify it using the path argument inside the webhook method `path="/customwebhook"`, by default the port is 8080
```py
from discord.ext import commands
import discordspy

bot = commands.Bot("!")
discords = discordspy.Client(bot, DISCORDS_TOKEN)
discords.webhook(port=2296, auth="password")

@bot.event
async def on_discords_server_post(status):
    if status == 200:
        print("Posted the server count:", discords.servers())

bot.run(TOKEN)
```