#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram import Updater, ReplyKeyboardMarkup
import logging
import pyUnipdbot
import ConfigParser


config = ConfigParser.ConfigParser()
config.read('settings.ini')
token = str(config.get('main', 'token'))

TOPCOMMANDS = ['start', 'home', 'help', 'botinfo',
               'mensa', 'aulastudio', 'biblioteca',
               'udupadova', 'diritto_studio']

commands = pyUnipdbot.commandList()

# Enable logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def home(bot, update):
    pyUnipdbot.writedb(update.message.to_dict())
    reply, markup = pyUnipdbot.home()
    bot.sendMessage(update.message.chat_id,
                    text=reply,
                    reply_markup=ReplyKeyboardMarkup(markup))


def botinfo(bot, update):
    pyUnipdbot.writedb(update.message.to_dict())
    reply, markup = pyUnipdbot.botInfo()
    bot.sendMessage(update.message.chat_id,
                    text=reply,
                    reply_markup=ReplyKeyboardMarkup(markup))


def mensa(bot, update):
    pyUnipdbot.writedb(update.message.to_dict())
    reply, markup = pyUnipdbot.mensa()
    bot.sendMessage(update.message.chat_id,
                    text=reply,
                    reply_markup=ReplyKeyboardMarkup(markup))


def aulastudio(bot, update):
    pyUnipdbot.writedb(update.message.to_dict())
    reply, markup = pyUnipdbot.aulastudio()
    bot.sendMessage(update.message.chat_id,
                    text=reply,
                    reply_markup=ReplyKeyboardMarkup(markup))


def biblioteca(bot, update):
    pyUnipdbot.writedb(update.message.to_dict())
    reply, markup = pyUnipdbot.biblioteca()
    bot.sendMessage(update.message.chat_id,
                    text=reply,
                    reply_markup=ReplyKeyboardMarkup(markup))


def dirittostudio(bot, update):
    pyUnipdbot.writedb(update.message.to_dict())
    reply, markup = pyUnipdbot.dirittostudio()
    bot.sendMessage(update.message.chat_id,
                    text=reply,
                    reply_markup=ReplyKeyboardMarkup(markup))


def udupadova(bot, update):
    pyUnipdbot.writedb(update.message.to_dict())
    reply, markup = pyUnipdbot.udupadova()
    bot.sendMessage(update.message.chat_id,
                    text=reply,
                    reply_markup=ReplyKeyboardMarkup(markup))


def replier(bot, update):
    pyUnipdbot.writedb(update.message.to_dict())
    command = str(update.message.text).replace('/', '')
    command.lower()
    reply, markup, lat, lon = pyUnipdbot.replier(command)
    bot.sendMessage(update.message.chat_id,
                    text=reply,
                    reply_markup=ReplyKeyboardMarkup(markup))
    if lat is not None and lon is not None:
        bot.sendLocation(update.message.chat_id,
                         latitude=lat,
                         longitude=lon)


def position(bot, update):
    msg = update.message.to_dict()
    pyUnipdbot.writedb(msg)
    try:
        usrCoord = msg['location']
        reply, markup = pyUnipdbot.position(usrCoord)
        bot.sendMessage(update.message.chat_id,
                        text=reply,
                        reply_markup=ReplyKeyboardMarkup(markup))
    except:
        pass


def error(bot, update, error):
    pyUnipdbot.writedb(update.message.to_dict())
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.addTelegramCommandHandler("help", home)
    dp.addTelegramCommandHandler("start", home)
    dp.addTelegramCommandHandler("home", home)

    dp.addTelegramCommandHandler("botinfo", botinfo)

    dp.addTelegramCommandHandler("mensa", mensa)
    dp.addTelegramCommandHandler("aulastudio", aulastudio)
    dp.addTelegramCommandHandler("biblioteca", biblioteca)
    dp.addTelegramCommandHandler("udupadova", udupadova)
    dp.addTelegramCommandHandler("diritto_studio", dirittostudio)

    for command in commands:
        dp.addTelegramCommandHandler(command, replier)

    dp.addTelegramMessageHandler(position)

    dp.addErrorHandler(error)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
