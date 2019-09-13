<h1 align="center">
  <a href="https://telegram.me/UnipdBot"><img src="https://github.com/marsDurden/UnipdBot/blob/master/logo.png" alt="UnipdBot" width="20%"></a>
  <br>
  UnipdBot
  <br>
</h1>

An unofficial Telegram bot for students of [University of Padua](http://www.unipd.it/) (Unipd) - try it at [@UnipdBot](https://telegram.me/UnipdBot)!


### Description

Simple Telegram bot for viewing timetables, menus and other info about studying in Padova

### Running the bot

Just some simple instructions if you want to test the bot

- `pip install -r requirements.txt`
- Rename settings.ini.sample to settings.ini
- Create an access token with Telegram's @Botfather and place it in `settings.ini`. 
- Create an access token with Botan (for analytics) and place it in `settings.ini`. 
- Run `create_localdb.py` to create a local `pickledb` database in which you'll store commands. 
- Switch into the `db` folder and run `python createdb_logs.py`.


### License and credits

Read [LICENSE](https://github.com/mikexine/UnipdBot/blob/master/LICENSE) file for @UnipdBot's license.

This bot uses also:

- [python-telegram-bot](https://github.com/leandrotoledo/python-telegram-bot)
- [beautifulsoup4](http://www.crummy.com/software/BeautifulSoup/)
- [requests](http://docs.python-requests.org/en/latest/)
- [pickledb](https://pythonhosted.org/pickleDB/)
- [geopy](https://github.com/geopy/geopy)
- [simplejson](https://pypi.python.org/pypi/simplejson/)
- [arrow](http://crsmithdev.com/arrow/)
- Python, Internet, Telegram, and all those nice things.

### Contact

For anything (bugs, contributing, saying hi!), contact me on Telegram at [@ThanksLory](https://telegram.me/ThanksLory)
