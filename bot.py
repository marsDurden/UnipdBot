#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler # ultimo aggiunto
from telegram import ReplyKeyboardMarkup, ParseMode, Bot, InlineKeyboardButton, InlineKeyboardMarkup # ultime 2 aggiunte
import logging
import pyUnipdbot
import ConfigParser
import pyOrarioParser

config = ConfigParser.ConfigParser()
config.read('settings.ini')
token = str(config.get('main', 'token'))
servicetoken = str(config.get('main', 'servicetoken'))
botAdminID = str(config.get('main', 'admin'))

TOPCOMMANDS = ['start', 'home', 'help', 'botinfo',
               'mensa', 'aulastudio', 'biblioteca',
               'udupadova', 'diritto_studio']

commands = pyUnipdbot.commandList()

# logging
if str(config.get('main', 'logging')) == "INFO":
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)
elif str(config.get('main', 'logging')) == "NONE":
    pass
else:
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG)

logger = logging.getLogger(__name__)


def home(bot, update):
    pyUnipdbot.writedb(update.message.to_dict())
    reply, markup = pyUnipdbot.home()
    bot.sendMessage(update.message.chat_id,
                    text=reply,
                    reply_markup=ReplyKeyboardMarkup(markup, resize_keyboard=True))


def botinfo(bot, update):
    pyUnipdbot.writedb(update.message.to_dict())
    reply, markup = pyUnipdbot.botInfo()
    bot.sendMessage(chat_id=update.message.chat_id,
                    text=reply,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=ReplyKeyboardMarkup(markup, resize_keyboard=True))


def mensa(bot, update):
    pyUnipdbot.writedb(update.message.to_dict())
    reply, markup = pyUnipdbot.mensa()
    bot.sendMessage(chat_id=update.message.chat_id,
                    text=reply,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=ReplyKeyboardMarkup(markup, resize_keyboard=True))


def aulastudio(bot, update):
    pyUnipdbot.writedb(update.message.to_dict())
    reply, markup = pyUnipdbot.aulastudio()
    bot.sendMessage(update.message.chat_id,
                    text=reply,
                    reply_markup=ReplyKeyboardMarkup(markup, resize_keyboard=True))


def biblioteca(bot, update):
    pyUnipdbot.writedb(update.message.to_dict())
    reply, markup = pyUnipdbot.biblioteca()
    bot.sendMessage(update.message.chat_id,
                    text=reply,
                    reply_markup=ReplyKeyboardMarkup(markup, resize_keyboard=True))


def dirittostudio(bot, update):
    pyUnipdbot.writedb(update.message.to_dict())
    reply, markup = pyUnipdbot.dirittostudio()
    bot.sendMessage(update.message.chat_id,
                    text=reply,
                    reply_markup=ReplyKeyboardMarkup(markup, resize_keyboard=True))


def udupadova(bot, update):
    pyUnipdbot.writedb(update.message.to_dict())
    reply, markup = pyUnipdbot.udupadova()
    bot.sendMessage(update.message.chat_id,
                    text=reply,
                    reply_markup=ReplyKeyboardMarkup(markup, resize_keyboard=True))

def orario(bot, update):
    bot.sendChatAction(chat_id=update.message.chat_id,
                       action="typing")
    pyUnipdbot.writedb(update.message.to_dict())
    reply, keyboard = pyOrarioParser.orarioSetup(update.message.chat_id, resetDate = True)
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.sendMessage(update.message.chat_id,
                    text=reply,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup)

def orarioButton(bot, update):
    query = update.callback_query
    if pyOrarioParser.newOrario(query.message.chat_id, query.data.replace("data-", "")):
        bot.sendChatAction(chat_id=query.message.chat_id,
                       action="typing")
        reply, keyboard = pyOrarioParser.orarioSaveSetting(query.message.chat_id, query.data)
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.editMessageText(text=reply,
                            chat_id=query.message.chat_id,
                            message_id=query.message.message_id,
                            parse_mode=ParseMode.MARKDOWN,
                            reply_markup=reply_markup)

def replier(bot, update):
    pyUnipdbot.writedb(update.message.to_dict())
    command = str(update.message.text).replace('/', '')
    command.lower()
    reply, markup, lat, lon = pyUnipdbot.replier(command)
    bot.sendMessage(chat_id=update.message.chat_id,
                    text=reply,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=ReplyKeyboardMarkup(markup, resize_keyboard=True))
    if lat is not None and lon is not None:
        bot.sendLocation(update.message.chat_id,
                         latitude=lat,
                         longitude=lon)


def position(bot, update):
    print "running position"
    msg = update.message.to_dict()
    pyUnipdbot.writedb(msg)
    try:
        usrCoord = msg['location']
        reply, markup = pyUnipdbot.position(usrCoord)
        bot.sendMessage(chat_id=update.message.chat_id,
                        text=reply,
                        parse_mode=ParseMode.MARKDOWN,
                        reply_markup=ReplyKeyboardMarkup(markup, resize_keyboard=True))
    except:
        pass


def simpleText(bot, update):
    #print "running simpletext"
    msg = update.message.to_dict()
    pyUnipdbot.writedb(msg)
    text = ""
    try:
        text = '*'+ str(msg['from']['first_name']) +' '+ str(msg['from']['last_name']) +'*\n@'+ str(msg['from']['username'])
        bot.sendMessage(chat_id=botAdminID,
                        parse_mode=ParseMode.MARKDOWN,
                        text=text)
        text = str(msg['from']['id'])
        bot.sendMessage(chat_id=botAdminID,
                        text=text)
    except:
        pass
    bot.forwardMessage(chat_id=botAdminID,
                       from_chat_id=update.message.chat_id,
                       message_id=update.message.message_id)


def admin_reply(bot, update, args):
    msg = update.message.to_dict()
    pyUnipdbot.writedb(msg)
    servicer = Bot(token=servicetoken)
    if update.message.from_user.id == int(botAdminID):
        try:
            tmp = "/reply " + args[0] + " "
            sent = bot.sendMessage(chat_id=args[0],
                                   text=(update.message.text).replace(tmp, ""))
            #servicer.sendMessage(chat_id=botAdminID, text=str(sent))
        except:
            servicer.sendMessage(chat_id=botAdminID, text="error happened") 
    else:
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="error - you're not powerful enough")



def error(bot, update, error):
    try:
        ch_id = str(botAdminID)
        starter = Bot(token=token)
        txt = "An error happened"
        starter.sendMessage(ch_id, text=txt)
    except:
        pass
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    #print dir(dp)

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("help", home))
    dp.add_handler(CommandHandler("start", home))
    dp.add_handler(CommandHandler("home", home))

    dp.add_handler(CommandHandler("botinfo", botinfo))

    dp.add_handler(CommandHandler("mensa", mensa))
    dp.add_handler(CommandHandler("aulastudio", aulastudio))
    dp.add_handler(CommandHandler("biblioteca", biblioteca))
    dp.add_handler(CommandHandler("udupadova", udupadova))
    dp.add_handler(CommandHandler("diritto_studio", dirittostudio))
    
    dp.add_handler(CommandHandler("orario", orario))
    dp.add_handler(CallbackQueryHandler(orarioButton))

    for command in commands:
        dp.add_handler(CommandHandler(command, replier))

    dp.add_handler(CommandHandler("reply", admin_reply, pass_args=True))

    dp.add_handler(MessageHandler([Filters.location], position))
    dp.add_handler(MessageHandler([Filters.text], simpleText))
    dp.add_handler(MessageHandler([Filters.audio], simpleText))
    dp.add_handler(MessageHandler([Filters.photo], simpleText))
    dp.add_handler(MessageHandler([Filters.document], simpleText))
    dp.add_handler(MessageHandler([Filters.sticker], simpleText))
    dp.add_handler(MessageHandler([Filters.video], simpleText))
    dp.add_handler(MessageHandler([Filters.voice], simpleText))
    dp.add_handler(MessageHandler([Filters.contact], simpleText))

    dp.add_error_handler(error)
    updater.start_polling()

    ch_id = str(botAdminID)
    starter = Bot(token=token)

    txt = "I'm starting"
    #starter.sendMessage(ch_id, text=txt)

    updater.idle()

    txt = "Bot stopped!"
    #starter.sendMessage(ch_id, text=txt)

if __name__ == '__main__':
    main()
