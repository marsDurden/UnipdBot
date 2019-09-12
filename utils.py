import sqlite3
from urllib.request import urlopen
from bs4 import BeautifulSoup
from telegram import InlineKeyboardButton

from config import supported_languages, default_language, db_path

# Funzioni per bot.py

# Convert lang abbreviation to unicode flag
# Es: 'it' -> italian flag
def flag(code):
    code = code.upper()
    OFFSET = 127462 - ord('A')
    return chr(ord(code[0]) + OFFSET) + chr(ord(code[1]) + OFFSET)

#
# Database operations
#
# - get_*
# - set_*
# - save_*
# 
def get_chat_id(update, as_int=False):
    try:
        ch_id = update.message.chat.id
    except:
        ch_id = update.callback_query.message.chat.id
    finally:
        return int(ch_id) if as_int else ch_id

def get_lang(update, u_id=None):
    # Database: Lingua
    if u_id is None: u_id = str(update.message.from_user.id)
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute("SELECT lang FROM Lingua WHERE u_id = ?", (u_id,))
    lang = cur.fetchone()
    if lang is not None and lang[0] != '':
        lang = lang[0]
    else:
        lang = default_language
    con.close()
    return lang

def get_user_settings(update, lang_list, u_id=None):
    if u_id is None: u_id = str(update.message.from_user.id)
    lang = flag(get_lang('', u_id=u_id))
    # Database: Orario
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    cur.execute("SELECT alarm FROM Orario WHERE u_id = ?", (u_id,))
    alarm_hour = cur.fetchone()[0]
    if alarm_hour is None:
        alarm = 'off'
        reply = lang_list[0].format(lang, alarm)
    else:
        alarm = 'on'
        reply = lang_list[5].format(lang, alarm_hour, alarm)
    alarm_btn = lang_list[1] if alarm == 'off' else lang_list[2]
    con.close()

    markup = [[InlineKeyboardButton(flag(_), callback_data='2-lang-'+_) for _ in supported_languages]]
    markup.append([InlineKeyboardButton(alarm_btn, callback_data='2-alarm-' + alarm), InlineKeyboardButton(lang_list[3], callback_data='1-orario')])
    return reply, markup

def get_enabled_alarm_users():
    # Database: Orario
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute("SELECT u_id, alarm FROM Orario WHERE alarm NOT NULL")
    r = cur.fetchall()
    con.close()
    return r

def set_lang(u_id, lang_code):
    if lang_code != get_lang('', u_id=u_id):
        con = sqlite3.connect(db_path)
        cur = con.cursor()
        cur.execute("UPDATE Lingua SET lang = ? WHERE u_id = ?", (lang_code, u_id))
        con.commit()
        con.close()
        return True
    else:
        return False

def set_alarm_value(u_id, hour):
    # Database: Orario
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute("UPDATE Orario SET alarm = ? WHERE u_id = ?", (hour, u_id))
    con.commit()
    con.close()

def save_msg(update):
    # Salva il messaggio inviato dall'utente
    u_id = update.message.from_user.id
    msg_id = update.message.message_id
    chat_id = get_chat_id(update)
    msg = update.message.text
    date = update.message.date

    # Database: Messaggi
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    # msg_id, u_id, chat_id, msg, date
    cur.execute("INSERT INTO Messaggi VALUES (?,?,?,?,?)", \
                (msg_id, u_id, chat_id, msg, date))
    con.commit()
    con.close()

def save_loc(update):
    # Salva la posizione inviata dall'utente
    u_id = update.message.from_user.id
    lat = update.message.location.latitude
    lon = update.message.location.longitude
    date = update.message.date

    # Database: Locations
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    # u_id, lat, lon, date
    cur.execute("INSERT INTO Locations VALUES (?,?,?,?)", \
                (u_id, lat, lon, date))
    con.commit()
    con.close()

def new_user(update):
    # Inserisce nel database il nuovo utente
    id = update.message.from_user.id
    first_name = update.message.from_user.first_name
    last_name = update.message.from_user.last_name
    username = update.message.from_user.username
    date = update.message.date
    lang = update.message.from_user.language_code
    lang = lang if lang in supported_languages else default_language

    # Database: Utenti
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute("SELECT * FROM Utenti WHERE u_id = ?", (id,))
    # Chesck if user already in table
    if cur.fetchone() is None:
        # u_id, username, first_name, last_name, date
        cur.execute("INSERT INTO Utenti VALUES (?,?,?,?,?)", \
            (id, username, first_name, last_name, date))
        # Language
        cur.execute("INSERT INTO Lingua VALUES (?,?)", (id, lang))
        con.commit()
    con.close()

# Search for books using Il Cerca Facile
def cerca_facile(key, lang_list):
    key = key.replace('\n','')
    contents = ''
    text = ''
    markup = None
    noResult = False
    try:
        contents = urlopen("http://catalogo.unipd.it/F/?func=find-e&LOCAL_BASE=sbp01&find_scan_code=FIND_WRD&request=" + str(key) + "&filter_code_4=WTY&filter_request_4=+").read()
    except:
        pass
    if contents != '' and key != '':
        soup = BeautifulSoup(contents, 'html.parser')
        del contents
        table = soup.find(lambda tag: tag.name=='table' and tag.has_attr('id') and tag['id']=="striped")
        rows = table.findAll(lambda tag: tag.name=='tr')
        del soup
        n = 0
        for i in range(11):
            try:
                tds = rows[i].findAll(lambda tag: tag.name=='td')
                [x.extract() for x in tds[4].findAll('script')]
                text += '*' + tds[4].text.replace('\n','').replace('*','').replace('_',' ') + '*\n'
                autore = tds[2].text
                if autore != '':
                    text += '_' + lang_list[1] + ': ' + autore.replace('_',' ').replace('\n','').replace('*','') + '_\n'
                for a in tds[6].findAll(lambda tag: tag.name=='a'):
                    text += '[' + a.text.split('(')[0] + '](http://catalogo.unipd.it' + a['href'] + ')\n'
                text += '[' + lang_list[2] + '](http://catalogo.unipd.it' + tds[0].a['href'] + ')\n\n'
                n += 1
            except:
                pass
        if text == '': noResult = True
        text = lang_list[3] + ' ' + str(n) + ' ' + lang_list[4] + ':\n' + text + lang_list[5]
        markup = {'text': lang_list[6], 'url': ("http://catalogo.unipd.it/F/?func=find-e&LOCAL_BASE=sbp01&find_scan_code=FIND_WRD&request=" + str(key) + "&filter_code_4=WTY&filter_request_4=+")}
    if noResult:
        text = lang_list[7] #"Non ho trovato nulla\nPer una ricerca più approfondita c'è il *Cercafacile*"
        markup = {'text': 'Il Cercafacile', 'url': "http://bibliotecadigitale.cab.unipd.it/bd/cercafacile"}
    if key == '':
        text = lang_list[0]
    return text, markup

if __name__ == '__main__':
    get_enabled_alarm_users()
