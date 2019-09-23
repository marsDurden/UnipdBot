import pickle, json, datetime, requests
from bs4 import BeautifulSoup
from geopy.distance import vincenty
from datetime import datetime
from threading import Timer

from config import uniopen_url

class Captions:
    def __init__(self, supported_languages, captions_path, quick=True):
        self.data = dict()

        self.columns = supported_languages
        self.default = 'it'

        self.path = captions_path

        # Update menu every 15 minutes
        self.update_thread = RepeatedTimer(60*15, self.update_mense)

        if quick:
            try:
                self.data = pickle.load( open( self.path + "captions.pkl", "rb" ) )
            except FileNotFoundError:
                self.update_json()
        else:
            self.update_json()
        
        self.daily_mensa = {'new': [], 'completed': []}

    def stop(self):
        self.update_thread.stop()

    def update_json(self):
        # Load languages json
        for filename in self.columns:
            with open(self.path + filename + '.json', 'r') as f:
                self.data[filename] = json.load(f)

        # Utils json
        with open(self.path + 'biblio.json', 'r') as f:
                self.data['sub_commands'] = json.load(f)

        for  filename in ['aule_studio', 'mense']:
            with open(self.path + filename + '.json', 'r') as f:
                a = json.load(f)
                self.data['sub_commands'] = {**self.data['sub_commands'], **a}

        with open(self.path + 'keyboard.json', 'r') as f:
                self.data['keyboard'] = json.load(f)

        #print(json.dumps(self.data['sub_commands'], indent=4))

        # Save as pickle
        pickle.dump( self.data, open( self.path + "captions.pkl", "wb" ) )

    def get_reply(self, name, lang=None):
        if lang is None: lang = self.default
        try:
            data = self.data[lang][name]
        except KeyError:
            data = self.data['sub_commands'][name]

        if data['type'] == 0: # Principali
            return data['reply']

        elif data['type'] == 1: # Biblioteche / aulestudio
            string = self.data[lang]['type-1-string']
            posti = ''
            # Get number of seats left
            if name == 'pinali':
                n = requests.get("http://zaphod.cab.unipd.it/pinali/PostiLiberiPinali.txt").text.replace(' ','').replace('\n','')
                posti = '_' + string[1] + ':_ ' + n + '\n'
            elif name == 'metelli':
                n = requests.get("http://zaphod.cab.unipd.it/psico/disponibilita.txt").text.replace(' ','').replace('\n','')
                posti = '_' + string[1] + ':_ ' + n + '\n'
            elif name == 'bibliogeo':
                n = requests.get("https://docs.google.com/spreadsheets/d/e/2PACX-1vRG83kEytkR_pNTo-aOLmxnvuQiHXVI926S6ZzIbyv2WOTV3emPF6Y70od3oUR3pJ1JZ8JxyG959vMw/pubhtml?gid=1179896160&single=true")
                n = BeautifulSoup(n.text, 'html.parser')
                n = n.findAll("td", {"class": "s1"})
                posti = '_' + string[1] + ':_ ' + n[0].text + '\n_' + string[2] + ':_ ' + n[1].text + '\n'
            elif name == 'matematica':
                n = requests.get("https://wss.math.unipd.it/biblioteca/posti_liberi.txt").text.replace('\n','')
                if n != 'dato non disponibile': posti = '_' + string[1] + ':_ ' + n + '\n'
            reply = string[0].format(data['title'], posti, data['address'], data['timetable'])
            dict_days = self.data[lang]['orario']['reply']['days']
            list_days = list(dict_days)
            for i, day in enumerate(dict_days.values()):
                reply = reply.replace(list_days[i], day)
            return reply

        elif data['type'] == 2: # Mense
            list_string = self.data[lang]['type-2-string']

            # Opened or closed pranzo/cena
            pranzo = '*' + list_string[1] + '* ' + list_string[3].format(data['pranzo']['apertura'], data['pranzo']['chiusura']) if data['pranzo']['aperta'] else '*' + list_string[2] + '*'
            cena = '*' + list_string[1] + '* ' + list_string[3].format(data['cena']['apertura'], data['cena']['chiusura']) if data['cena']['aperta'] else '*' + list_string[2] + '*'

            reply = list_string[0].format(data['nome'], data['indirizzo'], pranzo, cena)

            # Menu
            if datetime.utcnow().hour < 15: # Pranzo
                if data['pranzo']['primo'] != '':
                    reply += list_string[4].format(data['pranzo']['primo'], data['pranzo']['secondo'], data['pranzo']['contorno'])
                    if data['pranzo']['dessert'] != '':
                        reply += list_string[5].format(data['pranzo']['dessert'])
            else: # Cena
                if data['cena']['primo'] != '':
                    reply += list_string[4].format(data['cena']['primo'], data['cena']['secondo'], data['cena']['contorno'])
                    if data['cena']['dessert'] != '':
                        reply += list_string[5].format(data['cena']['dessert'])
            return reply

    def get_keyboard(self, name, lang=None, isGroup=False):
        if lang is None: lang = self.default

        # Keyboards
        if name == 'home':
            if not isGroup:
                markup = [['orario', 'mensa'],
                        ['biblioteca', 'aulastudio'],
                        ['diritto_studio', 'udupadova'],
                        ['vicino a te', 'botinfo']]
            else:
                markup = [['orario'],
                        ['mensa', 'aulastudio'],
                        ['biblioteca', 'udupadova'],
                        ['diritto_studio', 'botinfo']]

        elif name == 'mensa':
            markup = [["sanfrancesco", "piovego"],
                    ["agripolis", "acli"],
                    ["belzoni", "murialdo"],
                    ["forcellini", "home"]]

        elif name == 'aulastudio':
            markup = [["jappelli", "pollaio"],
                    ["titolivio", "galilei"],
                    ["marsala", "viavenezia"],
                    ["aulaSanGaetano", "reset"],
                    ["home"]]

        elif name == 'biblioteca':
            markup = [["bibliodiritto", "filosofia", "ingegneria"],
                    ["someda", "maldura", "matematica"],
                    ["storia", "metelli", "pinali"],
                    ["caborin", "cuzabarella", "universitaria"],
                    ["bibliochimica", "agribiblio", "bibliogeo"],
                    ["sangaetano", "liviano",  "bibliofarmacia"],
                    ["vbranca", "home"]]

        elif name ==  'diritto_studio':
            markup = [["borse", "tasse"],
                    ["200ore", "informami"],
                    ["home"]]

        elif name == 'udupadova':
            markup = [["faqlibretto", "erasmus"],
                    ["controguida", "cambiocorso"],
                    ["assembleaudu", "sedeudu"],
                    ["home"]]

        else:
            data = self.data['keyboard'][name]

            # Sostituisce i nomi dei bottoni inline
            if data['inline']:
                try:
                    for i, item in enumerate(self.data[lang][name]['markup'].values()):
                        data['markup'][str(i)]['text'] = item
                except KeyError:
                    pass

            return [_ for _ in data.values()]

        # Sostituisce i nomi dei comandi nella tastiera
        for i, row in enumerate(markup):
            for j, caption in enumerate(row):
                try:
                    markup[i][j] = self.data[lang]['commands'][caption]
                except (KeyError, TypeError):
                    try:
                        markup[i][j] = self.data[lang]['sub_commands'][caption]
                    except (KeyError, TypeError):
                        pass
                if ' ' not in markup[i][j]: markup[i][j] = '/' + markup[i][j]
        return markup

    def get_command_handlers(self, key):
        reply = []
        if key == 'sub_commands':
            commands = []
            for lang in self.columns:
                for item in self.data[lang]['sub_commands'].values():
                    commands.append(item)
        else:
            commands = [self.data[lang]['commands'][key] for lang in self.columns]
        for item in commands:
            if item not in reply:
                reply.append(item)
        return reply

    def inverse_command_map(self, key, lang=None):
        if lang == None: lang = self.default

        my_map = self.data[lang]['sub_commands']
        inv_map = {v: k for k, v in my_map.items()}
        return inv_map[key]

    def reply_position(self, usrCoord, lang=None):
        if lang is None: lang = self.default
        markup = []; nearDist = []; unit = ['km' for _ in range(3)]
        distDict = {'mensa': {}, 'aulastudio': {}, 'biblioteca': {}}
        tmp = distDict
        today = str(datetime.today().weekday())

        for item in [s.replace('/','') for t in self.get_keyboard('mensa', lang) for s in t]:
            if item != 'home':
                pranzo = self.data['sub_commands'][item]['pranzo']['aperta']
                cena = self.data['sub_commands'][item]['cena']['aperta']
                if cena or pranzo:
                    distDict['mensa'][item] = {"lat": self.data['keyboard'][item]['lat'], "lon": self.data['keyboard'][item]['lon']}

        for item in [s.replace('/','') for t in self.get_keyboard('biblioteca', lang) for s in t]:
            if item != 'home':
                # TODO controllare che la biblio sia aperta
                distDict['biblioteca'][item] = {"lat": self.data['keyboard'][item]['lat'], "lon": self.data['keyboard'][item]['lon']}

        for item in [s.replace('/','') for t in self.get_keyboard('biblioteca', lang) for s in t]:
            if item != 'home':
                distDict['aulastudio'][item] = {"lat": self.data['keyboard'][item]['lat'], "lon": self.data['keyboard'][item]['lon']}

        for key in distDict:
            for i in distDict[key]:
                lat = distDict[key][i]['lat']
                lon = distDict[key][i]['lon']
                tmp[key][i] = vincenty((usrCoord['latitude'],
                                        usrCoord['longitude']),
                                    (lat, lon)).kilometers

        nearMensa = min(tmp['mensa'], key=tmp['mensa'].get)
        nearAula = min(tmp['aulastudio'], key=tmp['aulastudio'].get)
        nearBiblio = min(tmp['biblioteca'], key=tmp['biblioteca'].get)

        nearDist.append(float(tmp['mensa'][nearMensa]))
        nearDist.append(float(tmp['aulastudio'][nearAula]))
        nearDist.append(float(tmp['biblioteca'][nearBiblio]))

        for i in range(len(nearDist)):
            if nearDist[i] < 1:
                nearDist[i] = nearDist[i]*1000
                unit[i] = 'm'

        str_lang = self.data[lang]['position']['reply']

        line1 = "- `" + str_lang[0] + "` " + str_lang[1] + ": *{}*, " + str_lang[2] + " _{:.0f}_ " + unit[0] + ".\n\n"
        line1 = line1.format(self.data['sub_commands'][nearMensa]['nome'], nearDist[0])

        line2 = "- `" + str_lang[3] + "` " + str_lang[1] + ": *{}*, " + str_lang[2] + " _{:.0f}_ " + unit[1] + ".\n\n"
        line2 = line2.format(self.data['sub_commands'][nearAula]['title'], nearDist[1])

        line3 = "- `" + str_lang[4] + "` " + str_lang[1] + ": *{}*, " + str_lang[2] + " _{:.0f}_ " + unit[2] + ".\n\n"
        line3 = line3.format(self.data['sub_commands'][nearBiblio]['title'], nearDist[2])

        reply = line1 + line2 + line3

        markup.append(['/'+nearMensa])
        markup.append(['/'+nearAula])
        markup.append(['/'+nearBiblio])
        markup.append(['/home'])

        return reply, markup

    def update_mense(self):
        # Update Mense
        html = requests.get('http://www.esupd.gov.it/it')
        #print(html.headers['Date'])
        html = BeautifulSoup(html.content, "html.parser")

        rows = html.find('table',attrs={"summary":"Di seguito sono illustrate le mense con i loro tempi di attesa e i link ai menu, ove disponibili"}).find_all("tr")
        #for tmp in rows:
            #print(tmp.text)
        mense = dict()
        for row in rows:
            name = row.find('th').text.lower().replace(' ','')
            if name == 'piox': name = 'acli'
            elif name == 'nordpiovego': name = 'piovego'
            if name != '':
                mense[name] = {"type": 2, "pranzo": {}, "cena": {}}
                for i, cell in enumerate(row.find_all('td')):
                    if i == 0: # Pranzo
                        mense[name]['pranzo'] = {"aperta": cell.span['class'][0] == 'open', \
                            "primo": "", "secondo": "", "contorno": "", "dessert": ""}
                    elif i == 1: # Cena
                        mense[name]['cena'] = {"aperta": cell.span['class'][0] == 'open', \
                            "primo": "", "secondo": "", "contorno": "", "dessert": ""}
                    elif i == 3: # Link menu
                        a = cell.find('a')
                        #print(name, a)
                        if a is not None:
                            html = requests.get('http://www.esupd.gov.it' + a['href'])
                            html = BeautifulSoup(html.content, "html.parser")
                            menu = html.find('div', attrs={'id': 'WebPartWPQ5'})

                            for i, portata in enumerate(menu.find_all('ul')):
                                text = [_.text.replace(':','').replace('*','').replace(',\r','').replace('\t','').replace('\n','').replace('\r\r',', ').replace('\r','') for _ in portata.find_all('li')]
                                if i == 0:   # Primo
                                    mense[name]['pranzo']['primo'] = ', '.join(text)
                                elif i == 1: # Secondo
                                    mense[name]['pranzo']['secondo'] = ', '.join(text)
                                elif i == 2: # Contorno
                                    mense[name]['pranzo']['contorno'] = ', '.join(text)
                                elif i == 3: # Dolce
                                    mense[name]['pranzo']['dessert'] = ', '.join(text)
                            
                            # Menù trovato -> aggiunge la mensa al daily_mensa
                            if name not in self.daily_mensa['completed'] and \
                               name not in self.daily_mensa['new']:
                                self.daily_mensa['new'].append(name)

        orari = [['piovego', 'Nord Piovego', 'viale Colombo 1', '11:30', '14:30'],
            ['agripolis', 'Agripolis', 'viale Università 16, Legnaro', '11:45', '14:30'],
            ['belzoni', 'Belzoni', 'Via Belzoni, 146', '11:45', '14:30'],
            ['murialdo', 'Murialdo', 'Via Grassi 42', '11:45', '14:30', '19:15', '20:45'],
            ['forcellini', 'Forcellini', 'Via Forcellini, 172', '11:45', '14:30'],
            ['acli', 'Acli - Pio X', 'Via Bonporti 20', '11:30', '14:30', '18:45', '21:00'],
            ['sanfrancesco', 'San Francesco', 'Via S. Francesco, 122', '', '']]

        for row in orari:
            mense[row[0]]['nome'] = row[1]
            mense[row[0]]['indirizzo'] = row[2]
            mense[row[0]]['pranzo']['apertura'] = row[3]
            mense[row[0]]['pranzo']['chiusura'] = row[4]
            try:
                mense[row[0]]['cena']['apertura'] = row[5]
                mense[row[0]]['cena']['chiusura'] = row[6]
            except:
                pass

        with open(self.path + 'mense.json', 'w') as outfile:
            json.dump(mense, outfile, indent=4)

        self.update_json()

class RepeatedTimer(object):
    def __init__(self, interval, function):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function()

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False

if __name__ == '__main__':
    from config import supported_languages, captions_path
    # Used as update script by cron
    a = Captions(supported_languages, captions_path, quick=False)
    #print(a.reply_position({'longitude': 11.891931, 'latitude': 45.407387}))
    #print(a.get_command_handlers('orario'))
    #print(a.get_command_handlers('sub_commands'))
    
    a.update_mense()
    
    #print(a.daily_mensa)
    #print(a.get_reply('acli'))
    
    a.stop()
