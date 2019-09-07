from urllib.request import urlopen
import json, datetime, sqlite3, pickle, subprocess, os, requests
from telegram import InlineKeyboardButton

from config import list_url, orario_url, orario_path, db_path, global_path

def save_to(path, string):
    with open(path, 'w') as f:
        f.write(string)
    return

def update_database():
    data = datetime.date.today().strftime('%d-%m-%Y')

    # Create directory tree
    # Anno >> Scuola >> Corso >> Anno di studi
    #subprocess.call([ 'rm', '--preserve-root', '-R', orario_path])
    subprocess.call(['mkdir', '-p', orario_path])
    
    # Elenco anni da combocall
    elenco_anni = urlopen(list_url + '?aa=1').read().decode("utf-8")
    elenco_anni = json.loads(elenco_anni.split('= ')[1].replace(';',''))
    
    save_to(orario_path + 'elenco_anni.json', json.dumps(elenco_anni, indent=4))

    for anno in elenco_anni:
        # Anno 2018/19
        os.chdir(global_path + orario_path)
        subprocess.call(['mkdir', '-p', anno])
        os.chdir(anno)
        
        combo = urlopen(list_url + '?sw=ec_&page=corsi&aa=' + str(anno)).read().decode("utf-8").split('\n')
        
        elenco_corsi = json.loads(combo[0][20:-2])
        
        scuole = combo[2][21:-2].split('{')
        scuole.pop(0)
        i = 0; elenco_scuole = '{'
        for scuola in scuole:
            elenco_scuole += '"' + str(i) + '":{' + scuola
            i += 1
        elenco_scuole = json.loads(elenco_scuole + '}')
        
        # Toglie i 'tutti gli anni'
        #for a in elenco_corsi:
            #for b in a['elenco']:
                #i = 0
                #while i < len(b['elenco_anni']):
                    #if b['elenco_anni'][i]['valore'][-1] == '0':
                        #b['elenco_anni'].pop(i)
                    #else:
                        #i += 1

        ## Toglie le entry vuote
        #i = 0
        #while i < len(elenco_scuole):
            #if elenco_scuole[i]['valore'] == '':
                #elenco_scuole.pop(i)
            #else:
                #i += 1
        
        save_to('./elenco_scuole.json', json.dumps(elenco_scuole, indent=4))
        save_to('./elenco_corsi.json', json.dumps(elenco_corsi, indent=4))
    
        for corso in elenco_corsi['elenco']:
            # Corso Ingegneria dell'informazione
            name = corso['label'].replace('/','_').replace('-','').replace(' ','_')
            #print(name)
            subprocess.call(['mkdir', '-p', corso['valore']])
            os.chdir(corso['valore'])
            subprocess.call(['touch', name])
            new_orario = dict()
            elenco_anni_corso = [a['valore'] for a in corso['elenco_anni']]

            for anno_studi in elenco_anni_corso:
                # Primo anno, secondo, ecc
                payload = (
                    ('form_type', 'corso'),
                    ('anno', anno),
                    ('scuola', corso['scuola']),
                    ('corso', corso['valore']),
                    ('anno2', ('0', anno_studi)), ('anno2', ('1', anno_studi)),
                    ('date', data ),
                    ('_lang', 'it'),
                    ('all_events', '1')
                )
                orario = requests.post(orario_url, data=payload)
                orario = json.loads(orario.content)
                print(json.dumps(orario, indent=4))
                orario = orario['celle']
                try:
                    if orario[0]["tipo"] == "chiusura_type": del orario[0]
                except:
                    pass
                orario = sorted(orario, key=lambda d: d["timestamp"])
                new_orario[anno_studi] = []
                for cella in orario:
                    try:
                        new_orario[anno_studi].append({'nome': cella['nome_insegnamento'], \
                            'orario': cella['orario'], 'giorno': cella['giorno'], \
                            'aula': cella['aula'], 'docente': cella['docente'], 'data': cella['data']})
                    except:
                        pass
            # Save orario
            save_to("./orario.json", json.dumps(new_orario, indent=4))
            os.chdir(global_path + orario_path + anno)
    os.chdir(global_path)

def findBetween(s, first, last):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def newOrario(idUser, data):
    con = sqlite3.connect(db_path)
    c = con.cursor()
    for row in c.execute('SELECT ultima_data FROM Orario WHERE u_id = ' + str(idUser) ):
        if row[0] is None:
            con.close()
            return True
        if data == row[0]:
            con.close()
            return False
    con.close()
    return True

def orarioSetup(idUser, lang_str, resetDate=False):
    # Anno >> Scuola >> Corso >> Anno di studi
    keyboard = []
    con = sqlite3.connect(db_path)
    c = con.cursor()
    # Inserisce l'utente se non e' registrato
    for row in c.execute('SELECT u_id FROM Orario WHERE u_id = ?', (str(idUser),)):
        break
    else:
        # Iserisce l'utente per la prima volta
        c.execute("INSERT INTO Orario(u_id, anno, scuola, corso, anno_studi, ultima_data, alarm) VALUES('" + str(idUser) + "',?,?,?,?,?,?)", (None, None, None, None, None, None))
        con.commit()
    # Guarda se l'utente e' gia' settato
    for row in c.execute('SELECT anno FROM Orario WHERE u_id = "' + str(idUser) + '"' ):
        if row[0] is None:
            for tmp1 in elenco_corsi:
                keyboard.append([InlineKeyboardButton(tmp1["label"], callback_data="anno-"+str(tmp1["valore"]) )])
            return "*" + lang_str['text'][0] + "*\n\n" + lang_str['text'][1], keyboard
        else:
            anno = row[0]
    for row in c.execute('SELECT scuola FROM Orario WHERE u_id = "' + str(idUser) + '"' ):
        if row[0] is None:
            for tmp1 in elenco_scuole:
                keyboard.append( [ InlineKeyboardButton(tmp1["label"].replace("Scuola di ",""), callback_data=tmp1["valore"]) ] )
            keyboard.append([InlineKeyboardButton("- reset -", callback_data="reset_orario") ])
            return "*" + lang_str['text'][0] + "*\n\n" + lang_str['text'][2], keyboard
        else:
            scuola = row[0]
    for row in c.execute('SELECT corso FROM Orario WHERE u_id = "' + str(idUser) + '"' ):
        if row[0] is None:
            for tmpAnno in elenco_corsi:
                if tmpAnno["valore"] == anno:
                    for tmpScuola in tmpAnno["elenco"]:
                        if tmpScuola["scuola"] == scuola:
                            keyboard.append( [ InlineKeyboardButton(tmpScuola["label"].split('- ', 1)[-1], callback_data="corso-"+tmpScuola["valore"]) ] )
            keyboard.append([InlineKeyboardButton("- reset -", callback_data="reset_orario") ])
            return "*" + lang_str['text'][0] + "*\n\n" + lang_str['text'][3], keyboard
        else:
            corso = row[0]
    for row in c.execute('SELECT anno_studi FROM Orario WHERE u_id = "' + str(idUser) + '"' ):
        if row[0] is None:
            for tmpAnno in elenco_corsi:
                if tmpAnno["valore"] == anno:
                    for tmpScuola in tmpAnno["elenco"]:
                        if tmpScuola["valore"] == corso:
                            for tmpCorso in tmpScuola["elenco_anni"]:
                                keyboard.append( [ InlineKeyboardButton(tmpCorso["label"], callback_data="anno_studi-"+tmpCorso["valore"]) ] )
            keyboard.append([InlineKeyboardButton("- reset -", callback_data="reset_orario") ])
            return "*" + lang_str['text'][0] + "*\n\n" + lang_str['text'][4], keyboard
        else:
            anno_studi = row[0]
    for row in c.execute('SELECT ultima_data FROM Orario WHERE u_id = "' + str(idUser) + '"' ):
        if row[0] is None:
            data = datetime.date.today().strftime('%d-%m-%Y')
        else:
            data = row[0]
    if resetDate:
        data = datetime.date.today().strftime('%d-%m-%Y')
        c.execute("UPDATE Orario SET ultima_data = '" + data + "' WHERE u_id = '" + str(idUser) + "'")
        con.commit()
    
    orario = json.load(open( orario_path + anno + '/' + corso + "/orario.json", "rb" ))
    orario = orario[anno_studi]

    reply2 = ""
    for cella in orario:
        try:
            if cella["data"] == data:
                reply2 += "*" + cella["nome"].replace('_',' ') + "\n" + lang_str['text'][6] + ": " + cella["orario"] \
                    + "*\n" + lang_str['text'][7] + ": _" + cella["aula"].replace('_',' ') + "_" \
                    + "\n" + lang_str['text'][8] + ": _" + cella["docente"] + "_\n\n"
        except:
            pass
    #print(json.dumps(orario, indent=4))

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

    giorni = list(lang_str['days'].values())
    reply1 = "*" + lang_str['text'][5] + " " + giorni[data.weekday()] + data.strftime(" %d/%m/%Y") + ":*\n"
    reply = ""
    if reply2 == "":
        reply = giorni[data.weekday()] + data.strftime(" %d/%m/%Y") + ":\n*" + lang_str['text'][9] + "*"
    else:
        reply = reply1 + reply2

    return reply, [[InlineKeyboardButton(btn1, callback_data=btn1Data),InlineKeyboardButton(btn2, callback_data=btn2Data),InlineKeyboardButton(btn3, callback_data=btn3Data),
                    InlineKeyboardButton(btn4, callback_data=btn4Data),InlineKeyboardButton(btn5, callback_data=btn5Data)],
                    [InlineKeyboardButton(lang_str['text'][10], callback_data="reset_orario"), InlineKeyboardButton(lang_str['text'][11], callback_data="settings-view")]]

def orarioSaveSetting(idUser, value, lang_str):
    con = sqlite3.connect(db_path)
    c = con.cursor()
    # Inserimento dati
    if "anno-" in value:
        c.execute("UPDATE Orario SET anno = '" + str(value).replace("anno-", "") + "' WHERE u_id = '" + str(idUser) + "'")
        con.commit()
        return orarioSetup(idUser, lang_str)
    if "Scuola" in value:
        c.execute("UPDATE Orario SET scuola = '" + str(value) + "' WHERE u_id = '" + str(idUser) + "'")
        con.commit()
        return orarioSetup(idUser, lang_str)
    if "corso-" in value:
        c.execute("UPDATE Orario SET corso = '" + str(value).replace("corso-", "") + "' WHERE u_id = '" + str(idUser) + "'")
        con.commit()
        return orarioSetup(idUser, lang_str)
    if "anno_studi-" in value:
        c.execute("UPDATE Orario SET anno_studi = '" + str(value).replace("anno_studi-", "") + "' WHERE u_id = '" + str(idUser) + "'")
        con.commit()
        return orarioSetup(idUser, lang_str, resetDate = True)
    if "reset_orario" == value:
        c.execute("DELETE FROM Orario WHERE u_id = '" + str(idUser) + "'")
        con.commit()
        return orarioSetup(idUser, lang_str)
    if "data-" in value:
        c.execute("UPDATE Orario SET ultima_data = '" + str(value).replace("data-", "") + "' WHERE u_id = '" + str(idUser) + "'")
        con.commit()
        return orarioSetup(idUser, lang_str)
    if value == "orario":
        return orarioSetup(idUser, lang_str)
    return "Error", [[InlineKeyboardButton("Error", callback_data="reset_orario")]]

if __name__ == '__main__':
    update_database()
