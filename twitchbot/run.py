from twitchbot import *
from auth import *

bot = TwitchBot(user=USER, admin=ADMIN)
bot.connect(host=HOST, port=PORT, auth=AUTH, channel=CHANNEL)
bot.run()
