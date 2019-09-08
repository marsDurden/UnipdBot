# Configuration file

# Bot token
bot_token = 'bot token here'
botAdminID = 123456789

# Orario
list_url = 'https://gestionedidattica.unipd.it/PortaleStudenti/combo_call.php'
orario_url = 'https://gestionedidattica.unipd.it/PortaleStudenti/grid_call.php'

# File locations
global_path = '/path/to/this/folder/'
db_path = 'database/database.db'
captions_path = 'database/languages/'
orario_path = 'database/orario/'

# User lang
supported_languages = ['it', 'gb']
default_language = 'it'

sub_commands = [
    # Biblioteca
    "bibliodiritto", "filosofia", "ingegneria", "someda", "maldura", "matematica", "storia", "metelli", "pinali", "caborin", "cuzabarella", "universitaria",
    "bibliochimica", "agribiblio", "bibliogeo", "sangaetano", "liviano",  "bibliofarmacia",
    # Mensa
    "sanfrancesco", "piovego", "agripolis", "acli", "belzoni", "murialdo", "forcellini",
    # Aulastudio
    "jappelli", "pollaio", "titolivio", "galilei", "marsala", "viavenezia", "vbranca", "reset", "aulaSanGaetano",
    # Udupadova
    "faqlibretto", "erasmus", "controguida", "cambiocorso", "assembleaudu", "sedeudu",
    # Dirittostudio
    "borse", "tasse", "200ore", "informami"]
