
from dating_bot import DatingBot
from config import access_token, community_token, db_config, dev_config

bot = DatingBot(access_token, community_token, db_config, dev_config)
bot.listen()




