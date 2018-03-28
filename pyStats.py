#!/usr/bin/python
# -*- coding: utf-8 -*-
import sqlite3 as lite
import arrow
import os

def stats():    
    con = lite.connect('db/logs.db')
    
    start = arrow.get(2018, 3, 19)
    end = arrow.utcnow()
    last_month = arrow.utcnow().replace(weeks=-2)
    user_msg = ""
    n_msg = ""
    
    
    cur = con.cursor()
    cur.execute("DELETE FROM log WHERE username = 'ThanksLory'")
    cur.execute("DELETE FROM log WHERE day = '0'")
    cur.execute("SELECT COUNT(DISTINCT u_id) FROM log")
    users = cur.fetchone()
    cur.execute("SELECT COUNT(DISTINCT ch_id) FROM log")
    chats = cur.fetchone()
    cur.execute('SELECT * FROM log')
    rows = cur.fetchall()
    cur.execute("DROP TABLE IF EXISTS date")
    cur.execute('''CREATE TABLE date (date text, msg_id int)''')
    for r in arrow.Arrow.range('day', start, end):
        today = str(r.date())
        cur.execute("SELECT COUNT(*) FROM log WHERE day LIKE ?",
                    (today + '%',))
        n = cur.fetchone()[0]
        cur.execute('INSERT INTO date VALUES (?,?)', (today, n))
        if arrow.get(r.date()) > last_month:
            n_msg += "%s, %s\n" % (today, n)
        #print r.date().month
        #print end.month
    user_msg += "\n--> %s users in %s chats" % (users[0], chats[0])
    
    cur.execute("SELECT COUNT(*) FROM orario_setting WHERE scuola='Scuola_di_Scienze'") #TODO prendere i nomi dal json
    scienze = cur.fetchone()
    cur.execute("SELECT COUNT(*) FROM orario_setting WHERE scuola='Scuola_di_Agraria_e_Medicina_Veterinaria'")
    agra = cur.fetchone()
    cur.execute("SELECT COUNT(*) FROM orario_setting WHERE scuola='Scuola_di_Economia_e_Scienze_Politiche'")
    scipol = cur.fetchone()
    cur.execute("SELECT COUNT(*) FROM orario_setting WHERE scuola='Scuola_di_Giurisprudenza'")
    legge = cur.fetchone()
    cur.execute("SELECT COUNT(*) FROM orario_setting WHERE scuola='Scuola_di_Ingegneria'")
    ing = cur.fetchone()
    cur.execute("SELECT COUNT(*) FROM orario_setting WHERE scuola='Scuola_di_Medicina_e_Chirurgia'")
    med = cur.fetchone()
    cur.execute("SELECT COUNT(*) FROM orario_setting WHERE scuola='Scuola_di_Psicologia'")
    psy = cur.fetchone()
    cur.execute("SELECT COUNT(*) FROM orario_setting WHERE scuola='Scuola_di_Scienze_Umane-_Sociali_e_del_Patrimonio_Culturale'")
    nulla = cur.fetchone()
    user_msg += "\n\n*>Utenti orario*\n Agraria e Vet: %s\n Economia e SciPol: %s\n Legge: %s\n Ingegneria: %s\n Medicina: %s\n Psicologia: %s\n Scienze: %s\n Scienze Umane: %s" % (agra[0],scipol[0],legge[0],ing[0],med[0],psy[0],scienze[0],nulla[0])
    tot = int(agra[0])+int(scienze[0])+int(scipol[0])+int(legge[0])+int(ing[0])+int(med[0])+int(psy[0])+int(nulla[0])
    user_msg += "\n _Totale: %s_\n" % (tot)

    cur.execute("SELECT COUNT(*) FROM log WHERE msg = '/mensa'")
    user_msg += '\n*>Frequenza comandi*\n mensa: ' + str(cur.fetchall()[0][0])
    cur.execute("SELECT COUNT(*) FROM log WHERE msg = '/aulastudio'")
    user_msg += '\n aulastudio: ' + str(cur.fetchall()[0][0])
    cur.execute("SELECT COUNT(*) FROM log WHERE msg = '/biblioteca'")
    user_msg += '\n biblioteca: ' + str(cur.fetchall()[0][0])
    cur.execute("SELECT COUNT(*) FROM log WHERE msg = '/udupadova'")
    user_msg += '\n udupadova: ' + str(cur.fetchall()[0][0])
    cur.execute("SELECT COUNT(*) FROM log WHERE msg = '/diritto_studio'")
    user_msg += '\n diritto studio: ' + str(cur.fetchall()[0][0])
    cur.execute("SELECT COUNT(*) FROM log WHERE msg = '/orario'")
    user_msg += '\n orario: ' + str(cur.fetchall()[0][0]) + '\n\n*>Mense*'

    mensa = {}
    cur.execute("SELECT COUNT(*) FROM log WHERE msg = '/sanfrancesco'")
    mensa['sanfrancesco'] =  cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM log WHERE msg = '/piovego'")
    mensa['piovego'] =  cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM log WHERE msg = '/agripolis'")
    mensa['agripolis'] =  cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM log WHERE msg = '/acli'")
    mensa['acli'] =  cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM log WHERE msg = '/belzoni'")
    mensa['belzoni'] =  cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM log WHERE msg = '/murialdo'")
    mensa['murialdo'] =  cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM log WHERE msg = '/forcellini'")
    mensa['forcellini'] =  cur.fetchone()[0]
    tot = 0
    for item in mensa.values():
        tot += item
    mensa = sorted(mensa.items(), key=lambda temp: temp[1], reverse=True)
    for item in mensa:
        user_msg += '\n ' + str(item[1]) + ', ' + str(int(float(item[1])/tot*100)) + '%  ' + item[0]
    
    size = ''
    try:
        size = '*Size log.db: ' + str(os.path.getsize('/home/udupd/UnipdBot/db/logs.db')/1024) + 'K*\n\n'
    except Exception as inst:
        print type(inst)     # the exception instance
        print inst.args      # arguments stored in .args
        print inst

    #print n_msg
    #print user_msg
    
    text = size + n_msg + user_msg
    return text

def search(key):
    con = lite.connect('db/logs.db')
    cur = con.cursor()
    cur.execute("DELETE FROM log WHERE username = 'ThanksLory'")
    cur.execute("DELETE FROM log WHERE day = '0'")

    cur.execute("SELECT DISTINCT u_id, username, first_name, last_name FROM log WHERE username LIKE '%" + str(key) + "%' OR first_name LIKE '%" + str(key) + "%' OR last_name LIKE '%" + str(key) + "%' OR u_id = '" + str(key) + "'")
    data = cur.fetchall()
    text = ''
    for i in data:
        text += 'ID: ' + i[0]
        if i[1] != '0': text += '\nUsername: @' + i[1]
        if i[2] != '0': text += '\nNome: ' + i[2]
        if i[3] != '0': text += '\nCognome: ' + i[3]
        text += '\n\n'

    return text

if __name__ == '__main__':
    #print stats()
    print search('marco')
