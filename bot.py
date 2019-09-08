import logging, pickle
from datetime import time, timedelta
from functools import wraps

# Telegram bot libraries
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import KeyboardButton, ReplyKeyboardMarkup, ParseMode, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError, Unauthorized, BadRequest, TimedOut, ChatMigrated, NetworkError

# Local files
from utils import *
from orario import *
import config
from captions import Captions

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Captions class handles languages
languages = Captions(config.supported_languages, config.captions_path)

# Decorators
def admin(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        # Set administrators of bot
        admins = [config.botAdminID]
        # Get user ID of message
        user_id = context.message.chat.id
        if user_id in admins:
            return func(update, context, *args, **kwargs)
        return
    return wrapped

def bottleneck(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        # Autoban system
        bans = []
        user_id = context.message.chat.id
        if user_id not in bans:
            return func(update, context, *args, **kwargs)
        else:
            return
    return wrapped

# Update Handlers
@bottleneck
def start(bot, update):
    # TODO User privacy disclaimer
    new_user(update)
    home(bot, update)

@bottleneck
def home(bot, update):
    chat_id = get_chat_id(update)
    reply = languages.get_reply('home', lang=get_lang(update))
    if chat_id > 0:
        markup = languages.get_keyboard('home', lang=get_lang(update))
        # Add location button to keyboard
        markup[3][0] = KeyboardButton(text=str(markup[3][0]), request_location=True)
        bot.sendMessage(chat_id=chat_id,
                    text=reply,
                    reply_markup=ReplyKeyboardMarkup(markup, resize_keyboard=True))
    else:
        markup = languages.get_keyboard('home', lang=get_lang(update), isGroup=True)
        bot.sendMessage(chat_id=chat_id,
                    text=reply,
                    reply_markup=ReplyKeyboardMarkup(markup, resize_keyboard=True))

@bottleneck
def mensa(bot, update):
    reply = languages.get_reply('mensa', lang=get_lang(update))
    markup = languages.get_keyboard('mensa', lang=get_lang(update))
    bot.sendMessage(chat_id=get_chat_id(update),
                    text=reply,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=ReplyKeyboardMarkup(markup, resize_keyboard=True))

@bottleneck
def aulastudio(bot, update):
    reply = languages.get_reply('aulastudio', lang=get_lang(update))
    markup = languages.get_keyboard('aulastudio', lang=get_lang(update))
    bot.sendMessage(chat_id=get_chat_id(update),
                    text=reply,
                    reply_markup=ReplyKeyboardMarkup(markup, resize_keyboard=True))

@bottleneck
def biblioteca(bot, update):
    reply = languages.get_reply('biblioteca', lang=get_lang(update))
    markup = languages.get_keyboard('biblioteca', lang=get_lang(update))
    bot.sendMessage(chat_id=get_chat_id(update),
                    text=reply,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=ReplyKeyboardMarkup(markup, resize_keyboard=True))

@bottleneck
def dirittostudio(bot, update):
    reply = languages.get_reply('diritto_studio', lang=get_lang(update))
    markup = languages.get_keyboard('diritto_studio', lang=get_lang(update))
    bot.sendMessage(chat_id=get_chat_id(update),
                    text=reply,
                    reply_markup=ReplyKeyboardMarkup(markup, resize_keyboard=True))

@bottleneck
def udupadova(bot, update):
    reply = languages.get_reply('udupadova', lang=get_lang(update))
    markup = languages.get_keyboard('udupadova', lang=get_lang(update))
    bot.sendMessage(chat_id=get_chat_id(update),
                    text=reply,
                    reply_markup=ReplyKeyboardMarkup(markup, resize_keyboard=True))

@bottleneck
def botinfo(bot, update):
    reply = languages.get_reply('botinfo', lang=get_lang(update))
    markup = [[InlineKeyboardButton('Source code on Github', url='https://github.com/marsDurden/UnipdBot')]]
    markup = InlineKeyboardMarkup(markup)
    bot.sendMessage(chat_id=get_chat_id(update),
                    text=reply,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=markup)

@bottleneck
def sub_command(bot, update):
    # Save message
    save_msg(update)

    chat_id = get_chat_id(update)
    command = str(update.message.text).replace('/', '').lower()
    try:
        command = languages.inverse_command_map(command, lang=get_lang(update))
    except KeyError:
        pass
    reply = languages.get_reply(command, lang=get_lang(update))
    if reply == '': reply = 'Testo da inserire'
    inline, markup, lat, lon = languages.get_keyboard(command, lang=get_lang(update))
    if inline:
        markup = [[InlineKeyboardButton(text=line['text'], url=line['url'])] for line in markup.values()]
        markup = InlineKeyboardMarkup(markup)
        bot.sendMessage(chat_id=chat_id,
                        text=reply,
                        parse_mode=ParseMode.MARKDOWN,
                        reply_markup=markup)
    else:
        bot.sendMessage(chat_id=chat_id,
                        text=reply,
                        parse_mode=ParseMode.MARKDOWN)

    if lat is not None and lon is not None:
        bot.sendLocation(chat_id=chat_id,
                         latitude=lat,
                         longitude=lon)

@bottleneck
def cerca(bot, update, args):
    # Save message
    save_msg(update)

    chat_id = get_chat_id(update)
    bot.sendChatAction(chat_id=chat_id,
                       action="typing")

    reply, markup = cerca_facile('%20'.join(args), languages.get_reply('cerca', lang=get_lang(update)))

    if markup is not None:
        markup =  [[InlineKeyboardButton(markup['text'], url=markup['url'])]]
        markup = InlineKeyboardMarkup(markup)
        bot.sendMessage(chat_id=chat_id,
                        text=reply,
                        parse_mode=ParseMode.MARKDOWN,
                        reply_markup=markup)
    else:
        bot.sendMessage(chat_id=chat_id,
                        text=reply,
                        parse_mode=ParseMode.MARKDOWN)

@bottleneck
def orario(bot, update):
    u_id = str(update.message.from_user.id)
    chat_id = update.message.chat_id
    lang_str = languages.get_reply('orario', lang=get_lang('', u_id=u_id))
    reply, keyboard = orarioSetup(chat_id, lang_str, resetDate=True)
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.sendMessage(chat_id=chat_id,
                    text=reply,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup)

def callbackButton(bot, update, job_queue, chat_data):
    query = update.callback_query
    u_id = str(query.from_user.id)
    chat_id = query.message.chat_id
    keyboard = None
    if 'settings-' in query.data:
        data = query.data.split('-')
        if data[1] == 'alarm':
            if data[2] == 'on':
                unset_alarm(str(chat_id), job_queue)
                set_alarm_value(u_id, False)
            else:
                set_alarm(str(chat_id), u_id, job_queue)
                set_alarm_value(u_id, True)
        elif data[1] == 'view':
            pass # View settings (coming from orario)
        else:
            # Lang code in data[1]
            changed = set_lang(u_id, data[1])
            if not changed: return
        reply, keyboard = get_user_settings(update, languages.get_reply('settings', lang=get_lang('', u_id=u_id)), u_id=u_id)
    elif query.data[:2] == "v-":
        reply, keyboard = seggio(query.data)
    elif newOrario(chat_id, query.data.replace("data-", "")):
        lang_str = languages.get_reply('orario', lang=get_lang('', u_id=u_id))
        reply, keyboard = orarioSaveSetting(chat_id, query.data, lang_str)
    elif query.data == 'error':
        home(bot, update)
    if keyboard is not None:
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.editMessageText(text=reply,
                        chat_id=chat_id,
                        message_id=query.message.message_id,
                        parse_mode=ParseMode.MARKDOWN,
                        reply_markup=reply_markup)

@bottleneck
def settings(bot, update):
    reply = languages.get_reply('settings', lang=get_lang(update))
    reply, keyboard = get_user_settings(update, reply)
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.sendMessage(chat_id=get_chat_id(update),
                    text=reply,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup)

@bottleneck
def daily_orario(bot, job):
    chat_id = job.context[0]
    u_id = job.context[0]
    lang_str = languages.get_reply('orario', lang=get_lang('', u_id=u_id))
    reply, keyboard = orarioSetup(chat_id, lang_str, resetDate=True)

    if lang_str['text'][9] in reply: return

    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.sendMessage(chat_id=chat_id,
                    text=reply,
                    parse_mode=ParseMode.MARKDOWN,
                    disable_notification=True,
                    reply_markup=reply_markup)

def set_alarm(chat_id, u_id, job_queue):
    try:
        # 0: lun, 1: mar, 2: mer, 3: gio, 4: ven
        job_queue.run_daily(daily_orario, time=time(8, 0, 0), days=(0, 1, 2, 3, 4), context=[chat_id, u_id])
        #j = job_queue.run_repeating(daily_orario, timedelta(seconds=8), context=[chat_id, u_id]) # For testing
    except (IndexError, ValueError):
        pass

def unset_alarm(chat_id, job_queue):
    for job in job_queue.jobs():
        if job.context[0] == chat_id:
            job.schedule_removal()

@bottleneck
def position(bot, update):
    # Save message
    save_loc(update)

    usrCoord = update.message.location
    reply, markup = languages.reply_position(usrCoord, lang=get_lang(update))
    bot.sendMessage(chat_id=get_chat_id(update),
                    text=reply,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=ReplyKeyboardMarkup(markup, resize_keyboard=True))

@bottleneck
def simpleText(bot, update):
    cmd = update.message.text.lower().strip().replace("\\","").replace("/","").replace("%","")
    inoltra = False
    if cmd in ['mensa', 'menu', 'menù']:
        mensa(bot, update)
    elif cmd in ['help','info', 'aiuto']:
        botinfo(bot, update)
    elif cmd in ['orari', 'orario']:
        orario(bot, update)
    elif cmd in ['biblioteca', 'biblio']:
        biblioteca(bot,update)
    elif cmd in ['home','start']:
        home(bot, update)
    elif cmd in ['aulastudio', 'aula studio', 'aule studio']:
        aulastudio(bot, update)
    elif cmd in ['impostazioni']:
        settings(bot, update)
    elif cmd in config.sub_commands:
        sub_command(bot, update)
    elif cmd == 'pio x':
        update.message.text = 'acli'
        sub_command(bot, update)
    elif cmd.find("sds") >= 0 or cmd.find("sindacato degli studenti") >= 0:
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="Sindacato degli Studenti?\nNe ho sentito parlare, non ho ancora avuto il piacere di conoscere il loro BOT")
        inoltra = True
    elif cmd in ['votare', 'votazioni', 'seggi', 'seggio', 'elezioni']:
        seggi(bot, update)
    else:
        inoltra = True

    if inoltra:
        # Save message
        save_msg(update)
        # Forward message to admin
        bot.forwardMessage(chat_id=config.botAdminID,
                           from_chat_id=update.message.chat_id,
                           disable_notification=True,
                           message_id=update.message.message_id)
        text = '<code>/reply ' + str(update.message.chat.id) + '</code>'
        bot.sendMessage(chat_id=config.botAdminID,
                        parse_mode=ParseMode.HTML,
                        disable_notification=True,
                        text=text)

@admin
def admin_forward(bot, update):
    bot.forwardMessage(chat_id=config.botAdminID,
                       from_chat_id=get_chat_id(update),
                       message_id=update.message.message_id)

@admin
def admin_reply(bot, update, args):
    msg = update.message.to_dict()
    servicer = Bot(token=config.bot_token)
    try:
        tmp = "/reply " + args[0] + " "
        sent = bot.sendMessage(chat_id=args[0],
                               text=(update.message.text).replace(tmp, ""))
        servicer.sendMessage(chat_id=config.botAdminID, text='Messaggio inviato a '+str(sent['chat']['first_name']))
    except:
        servicer.sendMessage(chat_id=config.botAdminID, parse_mode=ParseMode.MARKDOWN, text="*ERRORE*\nMessaggio non inviato") 

@admin
def admin_update(bot, update):
    languages.update_mense()
    bot.sendMessage(chat_id=config.botAdminID, text='Mense: updated\nJson reloaded')
    try:
        bot.send_document(chat_id=config.botAdminID, document=open('./../bot.tar.gz', 'rb'))
    except:
        pass

def error(bot, update, error):
    try:
        #starter = Bot(token=config.bot_token)
        bot.sendMessage(str(config.botAdminID),parse_mode=ParseMode.MARKDOWN, text=('*ERROR*\nID: `%s`\ntext: %s\ncaused error: _%s_' % (update['message']['chat']['id'], update['message']['text'], error)))
    except:
        pass
    logger.warn('Update "%s" caused error "%s"' % (update, error))

def load_jobs(jq):
    for u_id in get_enabled_alarm_users():
        set_alarm(u_id, u_id, jq)
    print("Jobs loaded")

def main():
    # Run bot
    # Create the Updater and pass it your bot's token.
    updater = Updater(config.bot_token)

    job_queue = updater.job_queue

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("home", home))

    dp.add_handler(CommandHandler(languages.get_command_handlers('help'), botinfo))

    dp.add_handler(CommandHandler(languages.get_command_handlers('botinfo'), botinfo))

    dp.add_handler(CommandHandler(languages.get_command_handlers('mensa'), mensa))

    dp.add_handler(CommandHandler(languages.get_command_handlers('aulastudio'), aulastudio))

    dp.add_handler(CommandHandler(languages.get_command_handlers('biblioteca'), biblioteca))

    dp.add_handler(CommandHandler(languages.get_command_handlers('udupadova'), udupadova))

    dp.add_handler(CommandHandler(languages.get_command_handlers('diritto_studio'), dirittostudio))

    dp.add_handler(CommandHandler(languages.get_command_handlers('cerca'), cerca, pass_args=True))

    dp.add_handler(CommandHandler(languages.get_command_handlers('impostazioni'), settings))

    # Subcommands
    dp.add_handler(CommandHandler(languages.get_command_handlers('sub_commands'), sub_command))

    dp.add_handler(CommandHandler(config.sub_commands, sub_command))

    # Orario
    dp.add_handler(CommandHandler(languages.get_command_handlers('orario'), orario))

    dp.add_handler(CallbackQueryHandler(callbackButton,
                                pass_job_queue=True,
                                pass_chat_data=True))

    # Vicino a me
    dp.add_handler(MessageHandler(Filters.location, position))

    # Admin
    dp.add_handler(CommandHandler("reply", admin_reply, pass_args=True))
    dp.add_handler(CommandHandler("update", admin_update))
    dp.add_handler(MessageHandler(Filters.text, simpleText))
    dp.add_handler(MessageHandler(Filters.audio, admin_forward))
    dp.add_handler(MessageHandler(Filters.photo, admin_forward))
    dp.add_handler(MessageHandler(Filters.document, admin_forward))
    dp.add_handler(MessageHandler(Filters.sticker, admin_forward))
    dp.add_handler(MessageHandler(Filters.video, admin_forward))
    dp.add_handler(MessageHandler(Filters.voice, admin_forward))
    dp.add_handler(MessageHandler(Filters.contact, admin_forward))

    # log all errors
    dp.add_error_handler(error)

    # Load user daily_orario jobs
    load_jobs(job_queue)

    # Start the Bot
    updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()

    # Stop update process in background
    languages.stop()

if __name__ == '__main__':
    main()
