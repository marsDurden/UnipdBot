#!/usr/bin/python
# -*- coding: utf-8 -*-
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import ReplyKeyboardMarkup, ParseMode, Bot, InlineKeyboardButton, InlineKeyboardMarkup
import logging
import pyUnipdbot, pyStats, pyOrarioParser, pyCerca
import ConfigParser
import create_localdb as pyUpdateDB

config = ConfigParser.ConfigParser()
config.read('settings.ini')
token = str(config.get('main', 'token'))
botAdminID = str(config.get('main', 'admin'))
janitorID = str(config.get('main', 'janitor'))

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
                    parse_mode=ParseMode.MARKDOWN)


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
        bot.sendChatAction(chat_id=query.message.chat_id, action="typing")
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
    if command == 'controguida':
        markup = [[InlineKeyboardButton('Controguida', url=markup)]]
        markup = InlineKeyboardMarkup(markup)
        bot.sendMessage(chat_id=update.message.chat_id,
                        text=reply,
                        parse_mode=ParseMode.MARKDOWN,
                        reply_markup=markup)
    elif command == 'borse':
        markup = markup.split()
        markup = [[InlineKeyboardButton('Bando a.a. 2017/18', url=markup[0])],[InlineKeyboardButton('Calcolatore tasse', url=markup[1])],[InlineKeyboardButton('FAQ utili', url=markup[2])]]
        markup = InlineKeyboardMarkup(markup)
        bot.sendMessage(chat_id=update.message.chat_id,
                        text=reply,
                        parse_mode=ParseMode.MARKDOWN,
                        reply_markup=markup)
    elif command == '200ore':
        markup = markup.split()
        markup = [[InlineKeyboardButton('Bando a.a. 2017/18', url=markup[0])],[InlineKeyboardButton('Graduatoria a.a. 2017/18', url=markup[1])],[InlineKeyboardButton('Regolamento', url=markup[2])]]
        markup = InlineKeyboardMarkup(markup)
        bot.sendMessage(chat_id=update.message.chat_id,
                        text=reply,
                        parse_mode=ParseMode.MARKDOWN,
                        reply_markup=markup)
    else:
        bot.sendMessage(chat_id=update.message.chat_id,
                        text=reply,
                        parse_mode=ParseMode.MARKDOWN)
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
    msg = update.message.to_dict()
    pyUnipdbot.writedb(msg)
    text = ""
    try:
        text = '*'+ str(msg['from']['first_name']) +' '+ str(msg['from']['last_name']) +'*\n@'+ str(msg['from']['username'])
        bot.sendMessage(chat_id=botAdminID,
                        parse_mode=ParseMode.MARKDOWN,
                        text=text)
    except:
        pass
    bot.forwardMessage(chat_id=botAdminID,
                       from_chat_id=update.message.chat_id,
                       message_id=update.message.message_id)
    try:
        text = str(msg['from']['id'])
        bot.sendMessage(chat_id=botAdminID,
                        text=text)
    except:
        pass

def cerca(bot, update):
    bot.sendChatAction(chat_id=update.message.chat_id,
                       action="typing")
    msg = update.message.to_dict()
    pyUnipdbot.writedb(msg)
    reply, markup = pyCerca.cerca((update.message.text).replace('/cerca ', ""))
    markup =  [[InlineKeyboardButton(markup['text'], url=markup['url'])]]
    markup = InlineKeyboardMarkup(markup)
    bot.sendMessage(chat_id=update.message.chat_id,
                    text=reply,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=markup)

def admin_reply(bot, update, args):
    msg = update.message.to_dict()
    #pyUnipdbot.writedb(msg)
    servicer = Bot(token=token)
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

def admin_stats(bot, update, args):
    try:
        text = pyStats.stats()
        if update.message.from_user.id == int(botAdminID):
            bot.sendMessage(chat_id=botAdminID, parse_mode=ParseMode.MARKDOWN, text=text)
            servicer = Bot(token=token)
            if args[0] == 'log': servicer.send_document(chat_id=botAdminID, document=open('/home/udupd/UnipdBot/db/logs.db', 'rb'))
            elif args[0] == 'bot': servicer.send_document(chat_id=botAdminID, document=open('/home/udupd/bot.tar.gz', 'rb'))
        elif update.message.from_user.id == int(janitorID):
            bot.sendMessage(chat_id=janitorID, parse_mode=ParseMode.MARKDOWN, text=text)
    except:
        pass

def admin_update(bot, update, args):
    if update.message.from_user.id == int(botAdminID):
        text = pyUpdateDB.main()
        bot.sendMessage(chat_id=botAdminID, text=text)

def admin_search(bot, update, args):
    msg = update.message.to_dict()
    if update.message.from_user.id == int(botAdminID):
        try:
            tmp = "/search "
            text = pyStats.search((update.message.text).replace(tmp, ""))
            if text == '': text = 'Trovato niente'
            sent = bot.sendMessage(chat_id=botAdminID,
                                   text=text)
        except Exception as inst:
            print type(inst)     # the exception instance
            print inst.args      # arguments stored in .args
            print inst

def error(bot, update, error):
    try:
        ch_id = str(botAdminID)
        starter = Bot(token=token)
        txt = "An error happened"
        starter.sendMessage(ch_id, text=('Update "%s" caused error "%s"' % (update, error)))
    except:
        pass
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

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
    dp.add_handler(CommandHandler("cerca", cerca))
    
    dp.add_handler(CommandHandler("orario", orario))
    dp.add_handler(CallbackQueryHandler(orarioButton))

    for command in commands:
        dp.add_handler(CommandHandler(command, replier))

    dp.add_handler(CommandHandler("reply", admin_reply, pass_args=True))
    dp.add_handler(CommandHandler("stats", admin_stats, pass_args=True))
    dp.add_handler(CommandHandler("update", admin_update, pass_args=True))
    dp.add_handler(CommandHandler("search", admin_search, pass_args=True))


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
    starter.sendMessage(ch_id, text=txt)

    updater.idle()

    txt = "Bot stopped!"
    starter.sendMessage(ch_id, text=txt)

if __name__ == '__main__':
    main()
