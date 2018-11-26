# BestLocationsBot
BestLocationsBot for Telegram helps to save places for further visiting. 

The bot is deployed at Heroku and you can find it by the link: https://t.me/BestLocationsBot 

If you want to run the app locally, you need to installl the dependecies:

```pip install -r requirements.txt```

Add TOKEN from telegram to your environment:

```export TELEGRAM_BOT_TOKEN="my value" ```

The app uses redis db, so you need to run it first:

```redis-server ```

Next, you can run the bot:

```python  telegram_bot.py```
