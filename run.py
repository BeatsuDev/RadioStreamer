from core.bot import RadioStreamer

if __name__ == '__main__':
    bot = RadioStreamer()

    bot.run(os.environ.get('BOT_TOKEN', '<--INSERT TOKEN-->'))
