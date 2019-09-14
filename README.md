<h1 align="center">
  <a href="https://telegram.me/UnipdBot"><img src="https://github.com/marsDurden/UnipdBot/blob/master/logo.png" alt="UnipdBot" width="20%"></a>
  <br>
  UnipdBot
  <br>
</h1>

An unofficial Telegram bot for students of [University of Padua](http://www.unipd.it/) (Unipd) - try it at [@UnipdBot](https://telegram.me/UnipdBot)!


### Description

Simple Telegram bot for viewing timetables, menus and other info about studying and living in Padua

### Running the bot

Just some simple instructions if you want to test the bot

- Run `python3 -m pip install -r requirements.txt`
- Rename `config-default.py` to `config.py`
- Create an access token with Telegram's [@BotFather](https://telegram.me/BotFather) and place it in `config.py`. 
- Place your Telegram ID in the variable `botAdminID` in `config.py`
- In the directory `/database` rename `database-default.db` to `database.db`
- Start the bot by running `python3 bot.py`


### License and credits

Read [LICENSE](https://github.com/marsDurden/UnipdBot/raw/master/LICENSE.md) file for @UnipdBot's license.

This bot uses also:

- [python-telegram-bot](https://github.com/leandrotoledo/python-telegram-bot)
- [beautifulsoup4](http://www.crummy.com/software/BeautifulSoup/)
- [requests](http://docs.python-requests.org/en/latest/)
- [pickledb](https://pythonhosted.org/pickleDB/)
- [geopy](https://github.com/geopy/geopy)
- Python, Internet, Telegram, and all those nice things.

### Contact

For anything (bugs, contributing, saying hi!), contact me on Telegram at [@ThanksLory](https://telegram.me/ThanksLory)
