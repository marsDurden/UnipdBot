import logging
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
                    level=logging.WARNING)

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
        user_id = update.message.chat.id
        if user_id in admins:
            return func(update, context, *args, **kwargs)
        return
    return wrapped

def autoban(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        # Autoban system TODO
        bans = []
        user_id = update.message.chat.id
        if user_id not in bans:
            return func(update, context, *args, **kwargs)
        else:
            return
    return wrapped

# Update Handlers
@autoban
def start(update, context):
    # TODO User privacy disclaimer
    new_user(update)
    home(update, context)

@autoban
def home(update, context):
    chat_id = get_chat_id(update)
    reply = languages.get_reply('home', lang=get_lang(update))
    if chat_id > 0:
        markup = languages.get_keyboard('home', lang=get_lang(update))
        # Add location button to keyboard
        markup[3][0] = KeyboardButton(text=str(markup[3][0]), request_location=True)
        context.bot.sendMessage(chat_id=chat_id,
                    text=reply,
                    reply_markup=ReplyKeyboardMarkup(markup, resize_keyboard=True))
    else:
        markup = languages.get_keyboard('home', lang=get_lang(update), isGroup=True)
        context.bot.sendMessage(chat_id=chat_id,
                    text=reply,
                    reply_markup=ReplyKeyboardMarkup(markup, resize_keyboard=True))

@autoban
def mensa(update, context):
    reply = languages.get_reply('mensa', lang=get_lang(update))
    markup = languages.get_keyboard('mensa', lang=get_lang(update))
    context.bot.sendMessage(chat_id=get_chat_id(update),
                    text=reply,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=ReplyKeyboardMarkup(markup, resize_keyboard=True))

@autoban
def aulastudio(update, context):
    reply = languages.get_reply('aulastudio', lang=get_lang(update))
    markup = languages.get_keyboard('aulastudio', lang=get_lang(update))
    context.bot.sendMessage(chat_id=get_chat_id(update),
                    text=reply,
                    reply_markup=ReplyKeyboardMarkup(markup, resize_keyboard=True))

@autoban
def biblioteca(update, context):
    reply = languages.get_reply('biblioteca', lang=get_lang(update))
    markup = languages.get_keyboard('biblioteca', lang=get_lang(update))
    context.bot.sendMessage(chat_id=get_chat_id(update),
                    text=reply,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=ReplyKeyboardMarkup(markup, resize_keyboard=True))

@autoban
def dirittostudio(update, context):
    reply = languages.get_reply('diritto_studio', lang=get_lang(update))
    markup = languages.get_keyboard('diritto_studio', lang=get_lang(update))
    context.bot.sendMessage(chat_id=get_chat_id(update),
                    text=reply,
                    reply_markup=ReplyKeyboardMarkup(markup, resize_keyboard=True))

@autoban
def udupadova(update, context):
    reply = languages.get_reply('udupadova', lang=get_lang(update))
    markup = languages.get_keyboard('udupadova', lang=get_lang(update))
    context.bot.sendMessage(chat_id=get_chat_id(update),
                    text=reply,
                    reply_markup=ReplyKeyboardMarkup(markup, resize_keyboard=True))

@autoban
def botinfo(update, context):
    reply = languages.get_reply('botinfo', lang=get_lang(update))
    markup = [[InlineKeyboardButton('Source code on Github', url='https://github.com/marsDurden/UnipdBot')]]
    markup = InlineKeyboardMarkup(markup)
    context.bot.sendMessage(chat_id=get_chat_id(update),
                    text=reply,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=markup)

@autoban
def sub_command(update, context):
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
        context.bot.sendMessage(chat_id=chat_id,
                        text=reply,
                        parse_mode=ParseMode.MARKDOWN,
                        reply_markup=markup)
    else:
        context.bot.sendMessage(chat_id=chat_id,
                        text=reply,
                        parse_mode=ParseMode.MARKDOWN)

    if lat is not None and lon is not None:
        context.bot.sendLocation(chat_id=chat_id,
                         latitude=lat,
                         longitude=lon)

@autoban
def cerca(update, context):
    # Save message
    save_msg(update)
    
    args = context.args

    chat_id = get_chat_id(update)
    context.bot.sendChatAction(chat_id=chat_id,
                       action="typing")

    reply, markup = cerca_facile('%20'.join(args), languages.get_reply('cerca', lang=get_lang(update)))

    if markup is not None:
        markup =  [[InlineKeyboardButton(markup['text'], url=markup['url'])]]
        markup = InlineKeyboardMarkup(markup)
        context.bot.sendMessage(chat_id=chat_id,
                        text=reply,
                        parse_mode=ParseMode.MARKDOWN,
                        reply_markup=markup)
    else:
        context.bot.sendMessage(chat_id=chat_id,
                        text=reply,
                        parse_mode=ParseMode.MARKDOWN)

@autoban
def settings(update, context):
    reply = languages.get_reply('settings', lang=get_lang(update))
    reply, keyboard = get_user_settings(update, reply)
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.sendMessage(chat_id=get_chat_id(update),
                    text=reply,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup)

@autoban
def orario(update, context):
    u_id = str(update.message.from_user.id)
    chat_id = update.message.chat_id
    lang_str = languages.get_reply('orario', lang=get_lang('', u_id=u_id))
    reply, keyboard = orarioSetup(chat_id, lang_str, resetDate=True)
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.sendMessage(chat_id=chat_id,
                    text=reply,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup)

def callback_orario(update, context):
    data = update.callback_query.data[2:]
    u_id = str(update.callback_query.from_user.id)
    chat_id = update.callback_query.message.chat_id
    lang_str = languages.get_reply('orario', lang=get_lang('', u_id=u_id))
    reply, keyboard = orarioSaveSetting(chat_id, data, lang_str)
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.editMessageText(text=reply,
                    chat_id=chat_id,
                    message_id=update.callback_query.message.message_id,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup)

def callback_settings(update, context):
    data = update.callback_query.data[2:].split('-')
    u_id = str(update.callback_query.from_user.id)
    chat_id = update.callback_query.message.chat_id
    if data[0] == 'alarm':
        if data[1] == 'on':
            # Chiude il job
            unset_job_orario(str(chat_id), context.job_queue)
            set_alarm_value(u_id, None)
        elif data[1] == 'off':
            # Scelta timing orario
            lang_list = languages.get_reply('settings', lang=get_lang('', u_id=u_id))
            markup = []
            for hour in [5, 7, 9, 12, 18, 21]:
                markup.append([InlineKeyboardButton(str(hour)+':00', callback_data='2-alarm-set-'+str(hour)+':00'), InlineKeyboardButton(str(hour)+':30', callback_data='2-alarm-set-'+str(hour)+':30'),
                       InlineKeyboardButton(str(hour+1)+':00', callback_data='2-alarm-set-'+str(hour+1)+':00'), InlineKeyboardButton(str(hour+1)+':30', callback_data='2-alarm-set-'+str(hour+1)+':30')])
            markup = InlineKeyboardMarkup(markup)
            context.bot.editMessageText(text=lang_list[5],
                    chat_id=chat_id,
                    message_id=update.callback_query.message.message_id,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=markup)
            return
        elif data[1] == 'set':
            set_job_orario(str(chat_id), u_id, context.job_queue, orario=data[2])
            set_alarm_value(u_id, data[2])
    elif data[0] == 'mensa':
        if data[1] == 'enable':
            # Scelta mensa
            mense_list = languages.get_keyboard('mensa')
            lang_list = languages.get_reply('settings', lang=get_lang('', u_id=u_id))
            markup = []
            for row in mense_list:
                for mensa in row:
                    if mensa != '/home':
                        markup.append([InlineKeyboardButton(mensa.replace('/',''), callback_data='2-mensa-set-'+mensa.replace('/',''))])
            markup = InlineKeyboardMarkup(markup)
            context.bot.editMessageText(text=lang_list[9],
                    chat_id=chat_id,
                    message_id=update.callback_query.message.message_id,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=markup)
            return
        elif data[1] == 'set':
            set_fav_mensa(u_id, data[2])
        elif data[1] == 'disable':
            set_fav_mensa(u_id, None)
    elif data[0] == 'lang':
        changed = set_lang(u_id, data[1])
        if not changed: return
    reply, keyboard = get_user_settings(update, languages.get_reply('settings', lang=get_lang('', u_id=u_id)), u_id=u_id)
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.editMessageText(text=reply,
                    chat_id=chat_id,
                    message_id=update.callback_query.message.message_id,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup)

def job_orario(context):
    chat_id = context.job.context[0]
    u_id = context.job.context[0]
    lang_str = languages.get_reply('orario', lang=get_lang('', u_id=u_id))
    reply, keyboard = orarioSetup(chat_id, lang_str, resetDate=True)
    
    # Check if orario is empty
    if lang_str['text'][9] in reply: return

    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.sendMessage(chat_id=chat_id,
                    text=reply,
                    parse_mode=ParseMode.MARKDOWN,
                    disable_notification=True,
                    reply_markup=reply_markup)

def set_job_orario(chat_id, u_id, job_queue, orario):
    try:
        # 0: lun, 1: mar, 2: mer, 3: gio, 4: ven
        orario = orario.split(':')
        job_queue.run_daily(job_orario, time=time(int(orario[0]), int(orario[1]), 0), days=(0, 1, 2, 3, 4), context=[chat_id, u_id])
        #job_queue.run_repeating(job_orario, timedelta(seconds=10), context=[chat_id, u_id]) # For testing
    except (IndexError, ValueError):
        pass

def unset_job_orario(chat_id, job_queue):
    for job in job_queue.jobs():
        try:
            if job.context[0] == chat_id:
                job.schedule_removal()
        except:
            pass

def job_mensa(context):
    while languages.daily_mensa['new']:
        mensa = languages.daily_mensa['new'].pop()
        print('Aggiornamento mensa', mensa)
        for user_id in get_fav_mensa_users(mensa):
            reply = languages.get_reply('mensa', lang=get_lang('', u_id=user_id))
            markup = languages.get_keyboard('mensa', lang=get_lang('', u_id=user_id))
            context.bot.sendMessage(chat_id=user_id, text=reply,
                                    parse_mode=ParseMode.MARKDOWN, disable_notification=True,
                                    reply_markup=ReplyKeyboardMarkup(markup, resize_keyboard=True))
        
        languages.daily_mensa['completed'].append(mensa)

def set_job_mensa(context):
    # Run job for 4 hours (= 14400 seconds) so 9:00 ~ 13:00
    context.job_queue.run_repeating(job_mensa, interval=14400)

@autoban
def position(update, context):
    # Save message
    save_loc(update)

    usrCoord = update.message.location
    reply, markup = languages.reply_position(usrCoord, lang=get_lang(update))
    context.bot.sendMessage(chat_id=get_chat_id(update),
                    text=reply,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=ReplyKeyboardMarkup(markup, resize_keyboard=True))

@autoban
def simpleText(update, context):
    cmd = update.message.text.lower().strip().replace("\\","").replace("/","").replace("%","")
    inoltra = False
    if cmd in ['mensa', 'menu', 'menù']:
        mensa(update, context)
    elif cmd in ['help','info', 'aiuto']:
        botinfo(update, context)
    elif cmd in ['orari', 'orario']:
        orario(update, context)
    elif cmd in ['biblioteca', 'biblio']:
        biblioteca(bot,update)
    elif cmd in ['home','start']:
        home(update, context)
    elif cmd in ['aulastudio', 'aula studio', 'aule studio']:
        aulastudio(update, context)
    elif cmd in ['impostazioni']:
        settings(update, context)
    elif cmd in config.sub_commands:
        sub_command(update, context)
    elif cmd == 'pio x':
        update.message.text = 'acli'
        sub_command(update, context)
    elif cmd.find("sds") >= 0 or cmd.find("sindacato degli studenti") >= 0:
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="Sindacato degli Studenti?\nNe ho sentito parlare, non ho ancora avuto il piacere di conoscere il loro BOT")
        inoltra = True
    elif cmd in ['votare', 'votazioni', 'seggi', 'seggio', 'elezioni']:
        seggi(update, context)
    else:
        inoltra = True

    if inoltra:
        # Save message
        save_msg(update)
        # Forward message to admin
        context.bot.forwardMessage(chat_id=config.botAdminID,
                           from_chat_id=update.message.chat_id,
                           disable_notification=True,
                           message_id=update.message.message_id)
        text = '<code>/reply ' + str(update.message.chat.id) + '</code>'
        context.bot.sendMessage(chat_id=config.botAdminID,
                        parse_mode=ParseMode.HTML,
                        disable_notification=True,
                        text=text)

def admin_forward(update, context):
    context.bot.forwardMessage(chat_id=config.botAdminID,
                       from_chat_id=get_chat_id(update),
                       message_id=update.message.message_id)
    text = '<code>/reply ' + str(update.message.chat.id) + '</code>'
    context.bot.sendMessage(chat_id=config.botAdminID,
                    parse_mode=ParseMode.HTML,
                    disable_notification=True,
                    text=text)

@admin
def admin_reply(update, context):
    args = context.args
    msg = update.message.to_dict()
    servicer = Bot(token=config.bot_token)
    try:
        tmp = "/reply " + args[0] + " "
        sent = context.bot.sendMessage(chat_id=args[0],
                               text=(update.message.text).replace(tmp, ""))
        servicer.sendMessage(chat_id=config.botAdminID, text='Messaggio inviato a '+str(sent['chat']['first_name']))
    except:
        servicer.sendMessage(chat_id=config.botAdminID, parse_mode=ParseMode.MARKDOWN, text="*ERRORE*\nMessaggio non inviato") 

@admin
def admin_update(update, context):
    languages.update_mense()
    context.bot.sendMessage(chat_id=config.botAdminID, text='Mense: updated\nJson reloaded')

def error(update, context):
    try:
        context.bot.sendMessage(str(config.botAdminID),parse_mode=ParseMode.MARKDOWN, text=('*ERROR*\nID: `%s`\ntext: %s\ncaused error: _%s_' % (update.message.chat_id, update.message.text, context.error)))
        logger.warn('Update "%s" caused error "%s"' % (update.message.text, context.error))
    except:
        context.bot.sendMessage(str(config.botAdminID),parse_mode=ParseMode.MARKDOWN, text=('*ERROR*\nID: `%s`\ntext: %s\ncaused error: _%s_' % (update.callback_query.message.chat_id, update.callback_query.data, context.error)))
        logger.warn('Update "%s" caused error "%s"' % (update.callback_query.data, context.error))
    finally:
        with open('error.log', 'a') as f:
            f.write(str(update))
            f.write('\n')
            f.write(str(context.error))
            f.write('\n\n\n')
            f.close()

def load_jobs(jq):
    # Daily orario
    for item in get_enabled_alarm_users():
        set_job_orario(item[0], item[0], jq, item[1])
    
    # Daily mensa
    jq.run_daily(set_job_mensa, time=time(9, 0, 0), days=(0, 1, 2, 3, 4))

def main():
    # Run bot
    # Create the Updater and pass it your bot's token.
    updater = Updater(config.bot_token, use_context=True)

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

    # Inline callbacks
    #
    # pattern | class
    #   0-    | admin
    #   1-    | orario
    #   2-    | settings
    #   3-    | beta-testing
    dp.add_handler(CallbackQueryHandler(callback_orario, pattern='^1-', pass_job_queue=True))
    dp.add_handler(CallbackQueryHandler(callback_settings, pattern='^2-', pass_job_queue=True))

    # Vicino a me
    dp.add_handler(MessageHandler(Filters.location, position))

    # Admin
    dp.add_handler(CommandHandler("reply", admin_reply, pass_args=True))
    dp.add_handler(CommandHandler("update", admin_update))
    
    dp.add_handler(MessageHandler(Filters.text | Filters.command, simpleText))
    
    dp.add_handler(MessageHandler(Filters.contact | Filters.voice    | Filters.video |
                                  Filters.sticker | Filters.document | Filters.photo |
                                  Filters.audio   | Filters.invoice, admin_forward))

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
