from aiogram import Router

from src.bot.filters.profile_filter import ProfileFilter

myprofile_router = Router(name='myprofile')

myprofile_router.message.filter(ProfileFilter())
