#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib2
import requests
import json
import sqlite3
import datetime
import ConfigParser
from telegram import InlineKeyboardButton

config = ConfigParser.ConfigParser()
config.read('settings.ini')
listUrl = str(config.get('orario', 'listUrl'))
orarioUrl = str(config.get('orario', 'orarioUrl'))

def findBetween( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def newOrario(idUser, data):
    con = sqlite3.connect("db/logs.db")
    c = con.cursor()
    for row in c.execute('SELECT ultima_data FROM orario_setting WHERE u_id = ' + str(idUser) ):
        if row[0] is None:
            con.close()
            return True
        if data == row[0]:
            con.close()
            return False
    con.close()
    return True

def orarioSetup(idUser, resetDate = False):
    # Anno >> Scuola >> Corso >> Anno di studi
    response = urllib2.urlopen(listUrl)
    html = response.read()
    con = sqlite3.connect("db/logs.db")
    c = con.cursor()
    # Inserisce l'utente se non e' registrato
    for row in c.execute('SELECT u_id FROM orario_setting WHERE u_id = "' + str(idUser) + '"' ):
        break
    else:
        # Iserisce l'utente per la prima volta
        c.execute("INSERT INTO orario_setting(u_id, anno, scuola, corso, anno_studi, ultima_data) VALUES('" + str(idUser) + "',?,?,?,?,?)", (None, None, None, None, None))
        con.commit()
    # Guarda se l'utente e' gia' settato
    for row in c.execute('SELECT anno FROM orario_setting WHERE u_id = "' + str(idUser) + '"' ):
        if row[0] is None:
            elenco_corsi = findBetween( str(html), "elenco_corsi = ", ";" )
            elenco_corsi = json.loads(elenco_corsi)
            keyboard = []
            for tmp1 in elenco_corsi:
                keyboard.append([InlineKeyboardButton(tmp1["label"], callback_data="anno-"+str(tmp1["valore"]) )])
            return "*Setup orario*\n\nScegli l'anno", keyboard
        else:
            anno = row[0]
    for row in c.execute('SELECT scuola FROM orario_setting WHERE u_id = "' + str(idUser) + '"' ):
        if row[0] is None:
            elenco_scuole = findBetween( str(html), "elenco_scuole = ", ";" )
            elenco_scuole = json.loads(elenco_scuole)
            keyboard = []
            for tmp1 in elenco_scuole:
                if tmp1["valore"] != "":
                    keyboard.append( [ InlineKeyboardButton(tmp1["label"].replace("Scuola di ",""), callback_data=tmp1["valore"]) ] )
            keyboard.append([InlineKeyboardButton("- reset -", callback_data="setting") ])
            return "*Setup orario*\n\nScegli la scuola", keyboard
        else:
            scuola = row[0]
    for row in c.execute('SELECT corso FROM orario_setting WHERE u_id = "' + str(idUser) + '"' ):
        if row[0] is None:
            elenco_corsi = findBetween( str(html), "elenco_corsi = ", ";" )
            elenco_corsi = json.loads(elenco_corsi)
            keyboard = []
            for tmpAnno in elenco_corsi:
                if tmpAnno["valore"] == anno:
                    for tmpScuola in tmpAnno["elenco"]:
                        if tmpScuola["scuola"] == scuola:
                            keyboard.append( [ InlineKeyboardButton(tmpScuola["label"].split('- ', 1)[-1], callback_data="corso-"+tmpScuola["valore"]) ] )
            keyboard.append([InlineKeyboardButton("- reset -", callback_data="setting") ])
            return "*Setup orario*\n\nScegli il corso", keyboard
        else:
            corso = row[0]
    for row in c.execute('SELECT anno_studi FROM orario_setting WHERE u_id = "' + str(idUser) + '"' ):
        if row[0] is None:
            elenco_corsi = findBetween( str(html), "elenco_corsi = ", ";" )
            elenco_corsi = json.loads(elenco_corsi)
            keyboard = []
            for tmpAnno in elenco_corsi:
                if tmpAnno["valore"] == anno:
                    for tmpScuola in tmpAnno["elenco"]:
                        if tmpScuola["valore"] == corso:
                            for tmpCorso in tmpScuola["elenco_anni"]:
                                keyboard.append( [ InlineKeyboardButton(tmpCorso["label"], callback_data="anno_studi-"+tmpCorso["valore"]) ] )
            keyboard.append([InlineKeyboardButton("- reset -", callback_data="setting") ])
            return "*Setup orario*\n\nScegli l'anno di studi", keyboard
        else:
            anno_studi = row[0]
    for row in c.execute('SELECT ultima_data FROM orario_setting WHERE u_id = "' + str(idUser) + '"' ):
        if row[0] is None:
            data = datetime.date.today().strftime('%d-%m-%Y')
        else:
            data = row[0]
    if resetDate:
        data = datetime.date.today().strftime('%d-%m-%Y')
        c.execute("UPDATE orario_setting SET ultima_data = '" + data + "' WHERE u_id = '" + str(idUser) + "'")
        con.commit()
    del html
    
    payload = (
        ('form_type', 'corso'),
        ('anno', anno),
        ('scuola', scuola),
        ('corso', corso),
        ('anno2', ('0', anno_studi)), ('anno2', ('1', anno_studi)),
        ('date', data ),
        ('_lang', 'it'),
        ('all_events', '1')
    )
    orario = requests.post(orarioUrl, data=payload)
    orario = json.loads(orario.content)
    #print json.dumps(orario, indent=4, sort_keys=True)    

    orario = orario["celle"]
    orario = sorted(orario, key=lambda d: d["timestamp"])
    reply2 = ""
    for cella in orario:
        if cella["data"] == data:
            reply2 += cella["nome_insegnamento"] + "\nore: " + cella["orario"] + "\naula: _" + cella["aula"] + "_\n\n"
    #print json.dumps(orarioOrdinato, indent=4, sort_keys=True) 

    data = datetime.datetime.strptime(data, '%d-%m-%Y')
    
    tmpDay = data - datetime.timedelta(days=2)
    btn1 = "« " + tmpDay.strftime('%d')
    btn1Data = "data-" + tmpDay.strftime('%d-%m-%Y')
    
    tmpDay = data - datetime.timedelta(days=1)
    btn2 = "< " + tmpDay.strftime('%d')
    btn2Data = "data-" + tmpDay.strftime('%d-%m-%Y')
    
    tmpDay = data
    btn3 = "· " + tmpDay.strftime('%d') + " ·"
    btn3Data = "data-" + tmpDay.strftime('%d-%m-%Y')
    
    tmpDay = data + datetime.timedelta(days=1)
    btn4 = tmpDay.strftime('%d') + " >"
    btn4Data = "data-" + tmpDay.strftime('%d-%m-%Y')
    
    tmpDay = data + datetime.timedelta(days=2)
    btn5 = tmpDay.strftime('%d') + " »"
    btn5Data = "data-" + tmpDay.strftime('%d-%m-%Y')
    
    giorni = {"Monday": "Lun", "Tuesday": "Mar", "Wednesday": "Mer", "Thursday": "Gio", "Friday": "Ven", "Saturday": "Sab", "Sunday": "Dom"}
    reply1 = "*Orario di " + giorni[data.strftime("%A")] + data.strftime(" %d/%m/%Y") + ":*\n"
    reply = ""
    if reply2 == "":
        reply = giorni[data.strftime("%A")] + data.strftime(" %d/%m/%Y") + ":\n*Oggi relax!*"
    else:
        reply = reply1 + reply2
    
    return reply, [[InlineKeyboardButton(btn1, callback_data=btn1Data),InlineKeyboardButton(btn2, callback_data=btn2Data),InlineKeyboardButton(btn3, callback_data=btn3Data),
                    InlineKeyboardButton(btn4, callback_data=btn4Data),InlineKeyboardButton(btn5, callback_data=btn5Data)],[InlineKeyboardButton("Cambia impostazioni corso", callback_data="setting")]]
   

def orarioSaveSetting(idUser, value):
    con = sqlite3.connect("/db/logs.db")
    c = con.cursor()
    # Inserimento dati
    if "anno-" in value:
        c.execute("UPDATE orario_setting SET anno = '" + str(value).replace("anno-", "") + "' WHERE u_id = '" + str(idUser) + "'")
        con.commit()
        return orarioSetup(idUser)
    if "Scuola" in value:
        c.execute("UPDATE orario_setting SET scuola = '" + str(value) + "' WHERE u_id = '" + str(idUser) + "'")
        con.commit()
        return orarioSetup(idUser)
    if "corso-" in value:
        c.execute("UPDATE orario_setting SET corso = '" + str(value).replace("corso-", "") + "' WHERE u_id = '" + str(idUser) + "'")
        con.commit()
        return orarioSetup(idUser)
    if "anno_studi-" in value:
        c.execute("UPDATE orario_setting SET anno_studi = '" + str(value).replace("anno_studi-", "") + "' WHERE u_id = '" + str(idUser) + "'")
        con.commit()
        return orarioSetup(idUser, resetDate = True)
    if "setting" in value:
        c.execute("DELETE FROM orario_setting WHERE u_id = '" + str(idUser) + "'")
        con.commit()
        return orarioSetup(idUser)
    if "data-" in value:
        c.execute("UPDATE orario_setting SET ultima_data = '" + str(value).replace("data-", "") + "' WHERE u_id = '" + str(idUser) + "'")
        con.commit()
        return orarioSetup(idUser)
    return "error", [[InlineKeyboardButton("error", callback_data="error")]] # TODO
