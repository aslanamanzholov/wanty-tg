from aiogram import Router

from src.bot.filters.dreams_filter import DreamsFilter

dreams_router = Router(name='dreams')
dreams_router.message.filter(DreamsFilter())
