from src.telegram import bot

if bot:
    from . import admin_handlers
    from . import callback_handlers
