#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib2
import sqlite3
from bs4 import BeautifulSoup

def cerca(key):
    key = key.replace('\n','')
    contents = ''
    text = ''
    markup = ''
    try:
        contents = urllib2.urlopen("http://catalogo.unipd.it/F/?func=find-e&LOCAL_BASE=sbp01&find_scan_code=FIND_WRD&request=" + str(key) + "&filter_code_4=WTY&filter_request_4=+").read()
    except:
        pass
    if contents != '':
        soup = BeautifulSoup(contents, 'html.parser')
        del contents
        table = soup.find(lambda tag: tag.name=='table' and tag.has_attr('id') and tag['id']=="striped") 
        rows = table.findAll(lambda tag: tag.name=='tr')
        #print rows[1]
        for i in range(10):
            try:
                tds = rows[i].findAll(lambda tag: tag.name=='td')
                [x.extract() for x in tds[4].findAll('script')]
                text += '*' + tds[4].text.replace('\n','').replace('*','') + '*\n_Autore: ' + tds[2].text.replace('\n','').replace('*','') + '_\n'
                for a in tds[6].findAll(lambda tag: tag.name=='a'):
                    text += '[' + a.text.split('(')[0] + '](http://catalogo.unipd.it' + a['href'] + ')\n'
                text += '[Scheda libro](http://catalogo.unipd.it' + tds[0].a['href'] + ')\n\n'
                
                markup = {'text': 'Risultati completi', 'url': ("http://catalogo.unipd.it/F/?func=find-e&LOCAL_BASE=sbp01&find_scan_code=FIND_WRD&request=" + str(key) + "&filter_code_4=WTY&filter_request_4=+")}
            except:
                pass
    if text == '':
        text = "Non ho trovato nulla\nPer una ricerca più approfondita c'è il *Cercafacile*"
        markup = {'text': 'Il Cercafacile', 'url': "http://bibliotecadigitale.cab.unipd.it/bd/cercafacile"}
    return text, markup
