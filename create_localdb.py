#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
import pickledb
from time import sleep
import ConfigParser

def main():    
    config = ConfigParser.ConfigParser()
    config.read('settings.ini')
    
    ch_id = str(config.get('main', 'admin'))
    
    xApi = config.get('uniopen', 'api-token')
    
    HEADERS = {'content-type': 'application/json',
              'x-api-key': str(xApi)}
    URL = str(config.get('uniopen', 'url'))
    
    db = pickledb.load('db/unipdbot.pickledb', False)
    
    mensa = requests.get(URL + 'mensa/', headers=HEADERS).json()
    #print 'Piovego: '
    #print mensa['piovego']
    del mensa['last_update']
    for key in mensa:
        if mensa[key]['calendario']['pranzo'] == 1:
            pranzo = True
        else:
            pranzo = False
        if mensa[key]['calendario']['cena'] == 1:
            cena = True
        else:
            cena = False
    
        if pranzo and cena:
            tmp = "oggi è *aperta* sia a pranzo che a cena"
        elif pranzo and not cena:
            tmp = "oggi è *aperta* solo a pranzo"
        elif cena and not pranzo:
            tmp = "oggi è aperta solo a cena"
    
        if mensa[key]['menu']['primo'][0] == "Menu non pubblicato su www.esupd.gov.it/":
            menu = ""
        elif mensa[key]['menu']['primo'][0] == "Niente menu, errore su www.esupd.gov.it/":
            menu = ""
        else:
            menu = "\n_PRIMO:_ %s\n_SECONDO:_ %s\n_CONTORNO:_ %s\n_DESSERT:_ %s" % \
                   (', '.join(mensa[key]['menu']['primo']),
                    ', '.join(mensa[key]['menu']['secondo']),
                    ', '.join(mensa[key]['menu']['contorno']),
                    ', '.join(mensa[key]['menu']['dessert']))
    
        if not pranzo and not cena:
            text = '*Mensa %s*\nIn %s.\nOggi la mensa è *chiusa*.\n' % \
                    (mensa[key]['nome'].encode("utf-8"),
                     mensa[key]['indirizzo'].encode("utf-8"))
            mensa[key]['coord']['lat'] = None
            mensa[key]['coord']['lon'] = None
        else:
            text = '*Mensa %s*\nIn %s, %s con orario: *%s*. \n' % \
                    (mensa[key]['nome'].encode("utf-8"),
                     mensa[key]['indirizzo'].encode("utf-8"),
                     tmp,
                     mensa[key]['orari'].encode("utf-8"))
            text = text + menu.encode("utf-8")
    
        db.set(key, {'text': text, 'keyboard': [['/mensa'], ['/home']],
                     'coord': mensa[key]['coord']})
    
    
    #print 'Mensa fatta'
    sleep(2)
    
    aulastudio = requests.get(URL + 'aulastudio/', headers=HEADERS).json()
    for key in aulastudio:
        text = "*Aula %s*\n_Posti:_ %s\nIndirizzo: %s\n_Orari:_ %s.\n" % \
               (aulastudio[key]['nome'].encode("utf-8"),
                aulastudio[key]['posti'].encode("utf-8"),
                aulastudio[key]['indirizzo'].encode("utf-8"),
                aulastudio[key]['orario'].encode("utf-8"))
        db.set(key, {'text': text, 'keyboard': [['/aulastudio'], ['/home']],
                     'coord': aulastudio[key]['coord']})
    
    #print 'Aula studio fatta'
    sleep(2)
    
    biblioteca = requests.get(URL + 'biblioteca/', headers=HEADERS).json()
    for key in biblioteca:
        if key == "metelli" or key == "pinali":
            text = "*%s*\nPosti liberi: %s\nIndirizzo: %s\n_Orari:_ %s.\n" % \
               (biblioteca[key]['nome'].encode("utf-8"),
                biblioteca[key]['posti'].encode("utf-8"),
                biblioteca[key]['indirizzo'].encode("utf-8"),
                biblioteca[key]['orario'].encode("utf-8"))
        elif key == "bibliogeo":
            text = "*%s*\nPosti liberi: %s\nNotebook liberi: %s\nIndirizzo: %s\n_Orari:_ %s.\n" % \
               (biblioteca[key]['nome'].encode("utf-8"),
                biblioteca[key]['posti'].encode("utf-8"),
                biblioteca[key]['notebook'].encode("utf-8"),
                biblioteca[key]['indirizzo'].encode("utf-8"),
                biblioteca[key]['orario'].encode("utf-8"))
        else:
            text = "*%s*\nIndirizzo: %s\n_Orari:_ %s.\n" % \
                   (biblioteca[key]['nome'].encode("utf-8"),
                    biblioteca[key]['indirizzo'].encode("utf-8"),
                    biblioteca[key]['orario'].encode("utf-8"))
        db.set(key, {'text': text, 'keyboard': [['/biblioteca'], ['/home']],
                     'coord': biblioteca[key]['coord']})
    #print 'Biblioteca fatta'
    sleep(2)
    
    #db.set('key', {'text': '', 'keyboard': ''})
    db.set('controguida', {'text': '*La Controguida* è la guida all’università che realizziamo ogni anno e consegniamo gratuitamente a tutte le nuove matricole dell’Università al momento dell’immatricolazione.\nContiene una serie di informazioni utili sull’università: diritto allo studio, tasse, aule studio, mense, vita universitaria e non solo.', 'keyboard': 'https://goo.gl/UX4uMP'})
    db.set('faqlibretto', {'text': '*Dubbi sul nuovo libretto online e sulle modalità di accettazione del voto su Uniweb?*\nPuoi consultare la guida sul rifiuto del voto https://goo.gl/8ffPpf o la nostra guida https://goo.gl/BvNCHr con domande e risposte utili!', 'keyboard': ''})
    db.set('assembleaudu', {'text': '*Che cos’è l’Udu?*\nL’Udu (Unione degli Universitari) è l’associazione che ha creato questo Bot: è il più grande sindacato studentesco universitario nazionale, e ha anche una base a Padova. Fare parte dell’Udu significa difendere i diritti degli studenti universitari, organizzare iniziative e dibattiti, proporre soluzioni ai tanti problemi quotidiani della vita universitaria, e tanto altro ancora. Settimanalmente, Studenti Per - Udu Padova, la base padovana dell’Udu, si riunisce in Assemblea al Circolo Reset ([sedeudu]), via Loredan 26, vicino al Portello. Se sei interessato a conoscere la realtà della nostra associazione, o semplicemente vuoi saperne di più su quello che facciamo, puoi restare aggiornata seguendo la nostra pagina Facebook https://www.facebook.com/studentiper.udupadova o iscrivendoti al nostro canale Telegram @udupadova', 'keyboard': ''})
    db.set('erasmus', {'text': '*Vuoi saperne di più sull’esperienza Erasmus?*\nPuoi lasciare il like alla nostra pagina Facebook “InfoErasmus” https://www.facebook.com/infoerasmus!\nAlcuni link utili sono disponibili sul sito dell’ateneo al link https://goo.gl/Yz96fq', 'keyboard': ''})
    db.set('cambiocorso', {'text': '*Hai dubbi sulle procedure relative al cambio corso?*\nPuoi leggere questa guida che abbiamo realizzato https://goo.gl/GC9gN6 o consultare la pagina del sito di Ateneo: https://goo.gl/tPJKkh', 'keyboard': ''})
    db.set('sedeudu', {'text': 'La “sede” dell’Udu Padova, come comunemente la chiamano i suoi militanti, è il *Circolo Reset*: un circolo culturale, sede di diverse associazioni tra cui Studenti Per - Udu Padova, la Rete degli Studenti Medi del Veneto, Libera ed Anpi, è in Via Loredan, 26 a Padova, a pochi passi dal Portello. E’ anche un’aula studio con WiFi gratuito e prese di corrente, aperta quotidianamente dalle 9 alle 20: se cerchi un posto dove studiare o rilassarti dopo lezione, passa a fare un giro!\nPer maggiori informazioni sulle attività che si svolgono settimanalmente al Circolo Reset, puoi restare aggiornato sulla pagina Facebook https://www.facebook.com/reset.padova', 'keyboard': ''})
    #print 'UDU Padova fatta'
    sleep(2)
    
    db.set('borse', {'text': "Le graduatorie relative alle *borse di studio regionali* per l’a.a. 2017/2018 sono tre: \n- iscritti al primo anno: https://goo.gl/vCLCE1;\n- studenti stranieri iscritti al primo anno: https://goo.gl/53vn1c;\n- iscritti ad anni successivi al primo: https://goo.gl/6Qhvwh;\n\nPer gli studenti iscritti al primo anno, la borsa verrà erogata in due rate, ma il pagamento della seconda avverrà verso metà ottobre 2018 e sarà subordinato alla registrazione, entro il 10 agosto 2018, di 20 CFU. Il mancato conseguimento di almeno 20 CFU entro il 30 novembre 2018 comporta la revoca della borsa di studio. Gli studenti iscritti dal secondo anno in poi saranno invece pagati in un'unica rata e, se idonei ma non percettori di borsa di studio, godranno gratuitamente del servizio di ristorazione.\nPer motivi eccezionali e documentati, il termine per il conseguimento dei crediti può essere posticipato fino al massimo di tre mesi.", 'keyboard': 'https://goo.gl/4TLc7W https://goo.gl/RYKH8E https://goo.gl/0zKqvj'})
    db.set('tasse', {'text': "L'importo della contribuzione dipende dall'ISEE, dal merito e dal corso di laurea. Per più informazioni consulta il prospetto tasse al link: https://goo.gl/mcvLY3. Per sapere se hai diritto a riduzioni, parziali o totali, leggi il bando esoneri 2017/2018: https://goo.gl/CDSgkZ. La prima rata scade il 30 Settembre 2017; la seconda rata scade il 15 Febbraio 2018; la terza rata scade il 16 Maggio 2018.", 'keyboard': ''})
    db.set('200ore', {'text': 'Ogni anno gli studenti possono concorrere per svolgere collaborazioni a tempo parziale con l’Ateneo, per una durata massima di 200 ore. Possono concorrere gli studenti regolarmente iscritti con idonei requisiti economici e di merito, ad esclusione di quelli iscritti al primo anno dei corsi di laurea triennale e magistrale a ciclo unico, oltre a quelli che frequentano a tempo parziale. Possono invece partecipare alla selezione gli studenti iscritti al primo anno dei corsi di laurea magistrale. L’eventuale collaborazione a tempo parziale non costituisce attività lavorativa ed è compatibile con l’attribuzione della borsa di studio regionale', 'keyboard': 'https://goo.gl/Qe9pYc https://goo.gl/xL7N7A https://goo.gl/Amyi89'})
    db.set('informami', {'text': 'Per rimanere informato sulle ultimissime novità riguardanti l’Università di Padova, clicca su @udupadova ed iscriviti al canale. Riceverai tutte le informazioni più importanti (scadenze, pubblicazioni graduatorie, novità, etc..) non appena queste saranno disponibili!', 'keyboard': ''})
    #print 'Diritto allo studio fatto\n'
    db.dump()
    return 'Database updated'
    
if __name__ == '__main__':
    main()