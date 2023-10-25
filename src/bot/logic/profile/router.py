from aiogram import Router

from src.bot.filters.profile_filter import ProfileFilter

myprofile_router = Router(name='My Profile')
myprofile_router.message.filter(ProfileFilter())
