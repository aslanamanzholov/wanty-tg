"""This file represents a My Profile logic."""
import emoji

from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from .router import myprofile_router
from src.bot.structures.fsm.dream_edit import DreamEditGroup
from src.bot.structures.keyboards.dreams import (
    DREAMS_MAIN_INLINE_MARKUP,
    DREAMS_NOT_FOUND_INLINE_MARKUP,
    CANCEL_BUTTON
)
from src.bot.structures.fsm.register import ChangeProfileName
from src.bot.structures.keyboards.menu import MENU_KEYBOARD, ADDITIONAL_FEATURES_MARKUP


@myprofile_router.message(F.text.lower() == "отмена")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()

    if current_state is not None:
        await state.clear()
        await message.answer(f"Вы отменили {emoji.emojize(':smiling_face_with_tear:')}",
                             reply_markup=DREAMS_NOT_FOUND_INLINE_MARKUP)


@myprofile_router.message(F.text.lower().startswith('изменить имя'))
@myprofile_router.message(F.text == f'Изменить имя {emoji.emojize(":writing_hand:")}')
async def dream_change_name_handler(message: types.Message, state: FSMContext):
    await state.set_state(ChangeProfileName.name)
    await message.answer(
        text="Введите новое имя, на которое хотите изменить",
        reply_markup=CANCEL_BUTTON,
        parse_mode='MARKDOWN'
    )


@myprofile_router.message(ChangeProfileName.name)
async def edit_dream_name_handler(message: types.Message, state: FSMContext, db):
    new_name = message.text

    user = await db.user.get_user_by_id(message.from_user.id)
    user.name = new_name
    await db.session.commit()

    await state.clear()

    await message.answer(
            text=f"Вы успешно поменяли имя на *{new_name}*",
            reply_markup=MENU_KEYBOARD,
            parse_mode='MARKDOWN'
        )


@myprofile_router.message(F.text.lower() == 'мои желания')
@myprofile_router.message(F.text == 'Мои желания')
@myprofile_router.message(F.text == 'Мои желания')
async def mydream_handler(message: types.Message, db):
    dreams_of_user = await db.dream.get_dreams_of_user(user_id=message.from_user.id)
    if dreams_of_user:
        for ind, dream in enumerate(dreams_of_user):
            reply_markup = types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [types.InlineKeyboardButton(text='Изменить', callback_data=f'edit_dream {dream.id}')],
                    [types.InlineKeyboardButton(text='Удалить', callback_data=f'delete_dream {dream.id}')]
                ]
            )
            text = (f"\n*Желание №{ind + 1}*\n\n"
                    f"*Тема*: {dream.name}\n"
                    f"*Описание*: {dream.description}\n\n")
            if dream.image:
                await message.bot.send_photo(message.chat.id,
                                             types.BufferedInputFile(dream.image,
                                                                     filename=f"user_photo_{dream.id}.png"),
                                             caption=text,
                                             reply_markup=reply_markup,
                                             parse_mode='MARKDOWN')
            else:
                await message.answer(text, reply_markup=reply_markup, parse_mode='MARKDOWN')

        # Перемещаем этот блок за пределы цикла
        await message.answer(
            f"*Вы также можете выбрать одно из следующих действий:* {emoji.emojize(':backhand_index_pointing_down:')}",
            reply_markup=MENU_KEYBOARD,
            parse_mode='MARKDOWN'
        )
    else:
        no_dreams_text = (
            "🌟 **У тебя пока нет желаний** 🌟\n\n"
            "Не переживай! Это отличная возможность создать свое первое желание.\n\n"
            "**🏆 Достижения:**\n"
            "• Создай первое желание и получи достижение 'Первый шаг' (+10 очков)\n"
            "• Начни свой путь к званию 'Мастер желаний'\n\n"
            "**💭 Что можно пожелать?**\n"
            "• Встречу с единомышленниками\n"
            "• Совместное путешествие\n"
            "• Новое хобби или увлечение\n"
            "• Помощь в достижении цели\n\n"
            "**🚀 Создай свое первое желание прямо сейчас!**\n"
            "Нажми кнопку 'Создать желание' ниже и начни зарабатывать очки!"
        )
        
        await message.answer(
            no_dreams_text,
            reply_markup=DREAMS_NOT_FOUND_INLINE_MARKUP,
            parse_mode="MARKDOWN"
        )


@myprofile_router.callback_query(F.data.startswith("edit_dream"))
async def myprofile_edit_dream_callback_handler(callback_query: types.CallbackQuery, state: FSMContext, db):
    dream_id = callback_query.data.split(' ')[1] or None
    await state.set_state(DreamEditGroup.name)
    await state.update_data(dream_id=dream_id)

    await callback_query.message.answer(
        f'{emoji.emojize(":speech_balloon:")} Напиши, как ты хочешь отредактировать название желания:',
        reply_markup=CANCEL_BUTTON,
    )


@myprofile_router.message(DreamEditGroup.name)
async def edit_dream_name_handler(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(DreamEditGroup.image)

    text = (
        "Отправьте изображение с желанием. "
        "Это поможет привлечь больше внимания и заинтересовать больше людей "
        f"{emoji.emojize(':thumbs_up:')} (не обязательное поле)"
    )

    await message.answer(text, reply_markup=CANCEL_BUTTON)


@myprofile_router.message(DreamEditGroup.image)
async def edit_dream_description_handler(message: types.Message, state: FSMContext):
    await state.update_data(image=message.photo)
    await state.set_state(DreamEditGroup.description)

    text = 'Опиши ниже подробности желания, на которое хочешь поменять 😉'
    await message.answer(text, reply_markup=CANCEL_BUTTON)


@myprofile_router.message(DreamEditGroup.description)
async def edit_user_dream_handler(message: types.Message, state: FSMContext, db):
    try:
        data = await state.get_data()
        dream_id = int(data.get('dream_id'))
        name = data.get('name')
        description = message.text
        image_data = data.get('image')
        image_content = None

        if image_data:
            photo = image_data[-1]
            photo_file = await message.bot.get_file(photo.file_id)
            photo_url = photo_file.file_path
            request_url = f"https://api.telegram.org/file/bot{getenv('BOT_TOKEN')}/{photo_url}"
            response = requests.get(request_url)

            if response.status_code == 200:
                image_content = response.content
            else:
                raise Exception("Failed to fetch image content")

        dream = await db.dream.get_dream_by_id(dream_id)
        dream.name = name
        dream.description = description
        dream.image = image_content if image_data else None

        await db.session.commit()
        await state.clear()

        await message.answer(
            '*Ты успешно обновил содержимое желания..\n\nОжидайте взаимных откликов*',
            reply_markup=DREAMS_NOT_FOUND_INLINE_MARKUP,
            parse_mode="MARKDOWN"
        )
    except Exception as e:
        print(f"Error in edit_user_dream_handler: {e}")
        await message.answer("Произошла ошибка при обновлении желания. Пожалуйста, попробуйте еще раз.")


@myprofile_router.callback_query(F.data.startswith("delete_dream"))
async def myprofile_delete_dream_callback_handler(callback_query: types.CallbackQuery, db):
    try:
        dream_id = int(callback_query.data.split(' ')[1])
        dream = await db.dream.get_dream_by_id(dream_id)

        if dream:
            await db.session.delete(dream)
            await db.session.commit()
            await callback_query.message.answer("*Желание успешно удалено*", parse_mode='MARKDOWN')
        else:
            await callback_query.message.answer("*Не могу найти желание :(*", parse_mode='MARKDOWN')
    except Exception as e:
        print(f"Error in myprofile_delete_dream_callback_handler: {e}")
        await callback_query.message.answer("*Произошла ошибка при удалении желания. Пожалуйста, "
                                            "попробуйте еще раз.*", parse_mode='MARKDOWN')


@myprofile_router.message(F.text.lower() == 'профиль')
@myprofile_router.message(F.text == '👤 Профиль')
@myprofile_router.message(F.text == '👤 Профиль')
async def profile_handler(message: types.Message, db):
    user = await db.user.get_user_by_id(message.from_user.id)
    user_dreams = await db.dream.get_dreams_of_user(user_id=message.from_user.id)
    
    # Получаем статистику из прогресса
    user_progress = await db.progress.get_user_progress(message.from_user.id)
    if not user_progress:
        user_progress = await db.progress.create_user_progress(message.from_user.id)
    
    total_dreams = user_progress.total_dreams
    total_likes = user_progress.total_likes_received
    
    # Определяем уровень активности
    if total_dreams == 0:
        activity_level = "🆕 Новичок"
        activity_emoji = "🌟"
    elif total_dreams <= 3:
        activity_level = "🚀 Активный"
        activity_emoji = "🔥"
    elif total_dreams <= 7:
        activity_level = "⭐ Продвинутый"
        activity_emoji = "💫"
    else:
        activity_level = "🏆 Эксперт"
        activity_emoji = "👑"
    
    profile_text = (
            f"👤 **Твой профиль в Wanty** 👤\n\n"
            f"**{activity_emoji} {activity_level}**\n\n"
            f"**📊 Статистика:**\n"
            f"• Создано желаний: **{total_dreams}**\n"
            f"• Получено лайков: **{total_likes}**\n"
            f"• Просмотрено желаний: **{user_progress.total_dreams_viewed}**\n"
            f"• Поставлено лайков: **{user_progress.total_likes_given}**\n"
            f"• Дней активности: **{user_progress.consecutive_days}**\n"
            f"• Дата регистрации: **{user.created_at.strftime('%d.%m.%Y') if user.created_at else 'Не указано'}**\n\n"
            
            f"**👤 Личная информация:**\n"
            f"• Имя: **{user.name if user.name else 'Не указано'}**\n"
            f"• ID: `{user.user_id}`\n\n"
            
            f"**🏆 Достижения:**\n"
            f"• Общие очки: **{user_progress.total_points}**\n\n"
            
            "**💡 Дополнительные функции:**\n"
            "Используй кнопки ниже для доступа к достижениям, категориям и статистике!"
        )
    
    # Создаем комбинированную клавиатуру: основные кнопки + inline кнопки
    from src.bot.structures.keyboards.dreams import DREAMS_MAIN_INLINE_MARKUP
    
    await message.answer(
        profile_text,
        reply_markup=DREAMS_MAIN_INLINE_MARKUP,
        parse_mode="MARKDOWN"
    )
    
    # Отправляем inline кнопки отдельным сообщением
    await message.answer(
        "🔧 **Дополнительные возможности:**",
        reply_markup=ADDITIONAL_FEATURES_MARKUP,
        parse_mode="MARKDOWN"
    )
