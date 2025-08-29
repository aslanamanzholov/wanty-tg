"""This file represents a Dreams logic."""
import logging

import emoji
import aiohttp
import hashlib

from aiogram import types
from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from src.bot.structures.keyboards.dreams import (
    DREAMS_MAIN_INLINE_MARKUP, 
    DREAMS_NOT_FOUND_INLINE_MARKUP,
    CATEGORY_SELECTION_MARKUP,
    CANCEL_BUTTON,
    REGISTRATION_REQUIRED_MARKUP
)
from src.bot.structures.keyboards.menu import MENU_KEYBOARD

from .router import dreams_router
from src.bot.structures.fsm.dream_create import DreamGroup
from src.bot.structures.fsm.register import RegisterGroup


async def get_image_content(photo, bot, redis_cache=None):
    """Асинхронно загружает изображение с кэшированием."""
    try:
        photo_file = await bot.get_file(photo.file_id)
        photo_url = photo_file.file_path
        
        # Создаем хеш для кэширования
        cache_key = hashlib.md5(photo_url.encode()).hexdigest()
        
        # Проверяем Redis кэш
        if redis_cache:
            cached_image = await redis_cache.get_image_cache(cache_key)
            if cached_image:
                return cached_image
        
        # Асинхронная загрузка изображения
        bot_token = bot.token
        request_url = f"https://api.telegram.org/file/bot{bot_token}/{photo_url}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(request_url) as response:
                if response.status == 200:
                    image_content = await response.read()
                    # Кэшируем в Redis
                    if redis_cache:
                        await redis_cache.set_image_cache(cache_key, image_content)
                    return image_content
                    
    except Exception as e:
        logging.error(f"Ошибка при загрузке изображения: {e}")
        return None
    
    return None


@dreams_router.message(F.text.lower() == "отмена")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()

    if current_state is not None:
        await state.clear()
        await message.answer(f"Вы отменили {emoji.emojize(':smiling_face_with_tear:')}",
                             reply_markup=DREAMS_NOT_FOUND_INLINE_MARKUP)


@dreams_router.message(F.text.lower().startswith('создать желание'))
async def process_create_command(message: types.Message, state: FSMContext, db):
    user = await db.user.user_register_check(active_user_id=message.from_user.id)

    if user:
        await state.set_state(DreamGroup.name)
        create_dream_text = (
            "✨ **Создание нового желания** ✨\n\n"
            "Отлично! Давай создадим твое желание, которое вдохновит других!\n\n"
            "**🎯 Зачем создавать желания:**\n"
            "• Найти единомышленников\n"
            "• Получить достижения и очки\n"
            "• Вдохновить других\n"
            "• Реализовать свои мечты\n\n"
            "**Шаг 1 из 5: Название** 📝\n"
            "Придумай короткое и яркое название для своего желания.\n\n"
            "**💡 Примеры:**\n"
            "• Хочу путешествовать по странам\n"
            "• Мечтаю научиться играть на гитаре\n"
            "• Ищу компанию для похода в горы\n\n"
            "**Напиши свое желание:**"
        )
        
        return await message.answer(
            create_dream_text,
            reply_markup=CANCEL_BUTTON,
            parse_mode="MARKDOWN"
        )
    else:
        await state.set_state(RegisterGroup.age)
        register_text = (
            "🔒 **Регистрация обязательна** 🔒\n\n"
            "Для создания желаний нужно сначала зарегистрироваться в боте.\n\n"
            "**📝 Что нужно указать:**\n"
            "• Возраст\n"
            "• Пол\n"
            "• Город\n"
            "• Имя\n\n"
                    "**🎯 После регистрации ты сможешь:**\n"
        "• Создавать желания и получать очки (+15 за каждое)\n"
        "• Разблокировать достижения\n"
        "• Изучать категории желаний\n"
        "• Отслеживать свой прогресс\n"
        "• Зарабатывать очки за активность\n\n"
            "**🚀 Начнем регистрацию?**\n"
            "Сколько тебе лет? Просто введи число."
        )
        
        return await message.answer(
            register_text,
            reply_markup=CANCEL_BUTTON,
            parse_mode="MARKDOWN"
        )


@dreams_router.message(DreamGroup.name)
async def dream_name_handler(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(DreamGroup.category)

    # Показываем выбор категории
    from src.bot.structures.keyboards.dreams import CATEGORY_SELECTION_MARKUP
    
    category_text = (
        "📂 **Шаг 2 из 5: Выбор категории** 📂\n\n"
        "Отлично! Теперь выбери категорию для своего желания.\n\n"
        "**🎯 Зачем нужна категория:**\n"
        "• Помогает найти единомышленников\n"
        "• Упрощает поиск по интересам\n"
        "• Дает бонусные очки за правильную категоризацию\n\n"
        "**💡 Выбери подходящую категорию:**"
    )

    await message.answer(
        category_text, 
        reply_markup=CATEGORY_SELECTION_MARKUP, 
        parse_mode="MARKDOWN"
    )


@dreams_router.message(DreamGroup.category)
async def dream_category_handler(message: Message, state: FSMContext):
    await state.update_data(category=message.text)
    await state.set_state(DreamGroup.description)

    description_text = (
        "📝 **Шаг 3 из 5: Описание** 📝\n\n"
        "Отлично! Теперь расскажи подробнее о своем желании.\n\n"
        "**💭 Что написать:**\n"
        "• Почему это важно для тебя\n"
        "• Что именно ты хочешь\n"
        "• Когда и где это можно реализовать\n"
        "• Какая помощь нужна\n\n"
        "**💡 Пример:**\n"
        "Хочу научиться играть на гитаре. Ищу учителя или единомышленника для совместных занятий. "
        "Могу заниматься по вечерам в центре города. Готов оплатить уроки или обменяться навыками."
    )

    await message.answer(description_text, reply_markup=CANCEL_BUTTON, parse_mode="MARKDOWN")


@dreams_router.message(DreamGroup.description)
async def dream_description_handler(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(DreamGroup.image)

    image_text = (
        "🖼️ **Шаг 4 из 5: Изображение** 🖼️\n\n"
        "Отлично! Теперь можешь добавить фото к своему желанию.\n\n"
        "**📸 Зачем нужно фото:**\n"
        "• Привлекает больше внимания\n"
        "• Помогает лучше понять твое желание\n"
        "• Увеличивает шансы найти единомышленников\n\n"
        "**💡 Что можно отправить:**\n"
        "• Фото места, где хочешь побывать\n"
        "• Изображение того, чему хочешь научиться\n"
        "• Картинка, которая вдохновляет\n\n"
        "**⚠️ Важно:** Фото не обязательно, но очень желательно!\n\n"
        "**🎯 Выберите действие:**"
    )
    
    # Создаем inline-клавиатуру с кнопкой "Без изображения"
    from src.bot.structures.keyboards.dreams import CANCEL_BUTTON
    
    image_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🖼️ Без изображения", callback_data="create_without_image")]
        ]
    )
    
    await message.answer(
        image_text,
        reply_markup=image_markup,
        parse_mode="MARKDOWN"
    )


@dreams_router.message(DreamGroup.image)
async def dream_image_handler(message: Message, state: FSMContext, db, redis_cache=None):
    data = await state.get_data()
    description = data.get('description', '')
    category = data.get('category', '')

    dream_image = None
    if message.photo:
        photo = message.photo[-1]
        # Передаем bot объект для работы с файлами
        dream_image = await get_image_content(photo, message.bot, redis_cache)
    elif message.text and message.text.lower() == "без изображения":
        # Пользователь выбрал создать желание без изображения
        dream_image = None
    else:
        # Если отправлен не фото и не "без изображения", просим отправить фото или выбрать опцию
        await message.answer(
            "📸 **Отправьте фото или выберите опцию:**\n\n"
            "• Отправьте фото для своего желания\n"
            "• Или нажмите кнопку 'Без изображения'",
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [types.InlineKeyboardButton(text="🖼️ Без изображения", callback_data="create_without_image")]
                ]
            ),
            parse_mode="MARKDOWN"
        )
        return

    # Создаем желание
    try:
        await db.dream.new(
            user_id=message.from_user.id,
            username=message.from_user.username,
            image=dream_image,
            name=data.get('name', ''),
            description=description,
            category=category
        )
    except Exception as e:
        logging.error(f"Error creating dream: {e}")
        await message.answer("Произошла ошибка при создании желания.")
        return
    
    # Добавляем очки и проверяем достижения
    try:
        await db.progress.increment_dreams(message.from_user.id, 15)
        
        # Проверяем, нужно ли разблокировать достижение "Первый шаг"
        if not await db.achievements.is_achievement_unlocked(message.from_user.id, "first_dream"):
            await db.achievements.unlock_achievement(message.from_user.id, "first_dream", 10)
            await db.progress.increment_dreams(message.from_user.id, 10)  # Дополнительные очки за достижение
    except Exception as e:
        logging.warning(f"Could not update achievements for user {message.from_user.id}: {e}")
        # Продолжаем выполнение, даже если достижения не обновились
    
    await state.clear()
    success_text = (
        "🎉 **Желание успешно создано!** 🎉\n\n"
        f"**📂 Категория:** {category}\n\n"
        "Поздравляем! Твое желание теперь доступно всем пользователям Wanty.\n\n"
        "**🏆 Достижения:**\n"
        "• +15 очков за создание желания\n"
        "• Возможно, ты разблокировал новое достижение!\n\n"
        "**✨ Что дальше?**\n"
        "• Жди откликов от единомышленников\n"
        "• Получай уведомления о лайках\n"
        "• Создавай новые желания\n"
        "• Просматривай желания других\n\n"
        "**💡 Совет:** Будь активным! Чем больше ты взаимодействуешь с другими, тем больше шансов найти единомышленников и получить достижения!"
    )
    
    await message.answer(
        success_text,
        reply_markup=DREAMS_NOT_FOUND_INLINE_MARKUP,
        parse_mode="MARKDOWN"
    )


# Убираем глобальную переменную - теперь используем Redis кэш


async def edit_message_with_dream(message, dream, db, user=None):
    """Edit existing message with new dream content."""
    try:
        dream_user = await db.user.get_user_by_id(user_id=dream.user_id)
        user_gender = emoji.emojize(':man:') if dream_user and dream_user.gender == 'Мужчина' else emoji.emojize(':woman:')
        formatted_date = dream.created_at.strftime("%d.%m.%Y")

        text = (
            f"\n*Тема*: {dream.name}\n"
            f"*Описание*: {dream.description}\n"
            f"*Категория*: {dream.category if dream.category else 'Не указана'}\n"
            f"*Город*: {dream_user.country if dream_user else 'Другой'}\n"
            f"*Автор*: {dream_user.name if dream_user else 'Анонимный'} {user_gender}\n"
            f"*Дата создания*: {formatted_date}"
        )

        # Выбираем клавиатуру в зависимости от статуса регистрации пользователя
        if user:
            # Зарегистрированный пользователь - показываем кнопки лайк/дизлайк
            from src.bot.structures.keyboards.dreams import DREAMS_MAIN_INLINE_MARKUP
            reply_markup = DREAMS_MAIN_INLINE_MARKUP
        else:
            # Незарегистрированный пользователь - показываем только кнопку регистрации
            from src.bot.structures.keyboards.dreams import REGISTRATION_REQUIRED_MARKUP
            reply_markup = REGISTRATION_REQUIRED_MARKUP

        if dream.image:
            # Если есть изображение, отправляем новое сообщение с фото
            await message.bot.send_photo(
                message.chat.id,
                types.BufferedInputFile(dream.image, filename=f"user_photo_{dream.id}.png"),
                caption=text,
                reply_markup=reply_markup,
                parse_mode='MARKDOWN'
            )
            # Удаляем старое сообщение
            try:
                await message.delete()
            except Exception as e:
                logging.warning(f"Could not delete old message: {e}")
        else:
            # Если нет изображения, редактируем текст
            await message.edit_text(
                text,
                reply_markup=reply_markup,
                parse_mode='MARKDOWN'
            )
            
    except Exception as e:
        logging.error(f"Error editing message with dream: {e}")
        raise e


async def dreams_view_func(dream, message, db, user=None):
    if not dream:
        no_dreams_text = (
            "😔 **Больше желаний не найдено** 😔\n\n"
            "Похоже, ты просмотрел все доступные желания в данный момент.\n\n"
            "**💡 Что можно сделать:**\n"
            "• Создать свое желание (+15 очков)\n"
            "• Вернуться в главное меню\n\n"
            "**🌟 Совет:** Возможно, стоит создать свое желание и вдохновить других! Это принесет тебе очки и поможет разблокировать достижения!"
        )
        from src.bot.structures.keyboards.dreams import DREAMS_NOT_FOUND_INLINE_MARKUP
        await message.answer(no_dreams_text, reply_markup=DREAMS_NOT_FOUND_INLINE_MARKUP, parse_mode="MARKDOWN")
        return

    dream_user = await db.user.get_user_by_id(user_id=dream.user_id)
    user_gender = emoji.emojize(':man:') if dream_user and dream_user.gender == 'Мужчина' else emoji.emojize(':woman:')
    formatted_date = dream.created_at.strftime("%d.%m.%Y")

    text = (
        f"\n*Тема*: {dream.name}\n"
        f"*Описание*: {dream.description}\n"
        f"*Категория*: {dream.category if dream.category else 'Не указана'}\n"
        f"*Город*: {dream_user.country if dream_user else 'Другой'}\n"
        f"*Автор*: {dream_user.name if dream_user else 'Анонимный'} {user_gender}\n"
        f"*Дата создания*: {formatted_date}"
    )

    # Выбираем клавиатуру в зависимости от статуса регистрации пользователя
    if user:
        # Зарегистрированный пользователь - показываем кнопки лайк/дизлайк
        from src.bot.structures.keyboards.dreams import DREAMS_MAIN_INLINE_MARKUP
        reply_markup = DREAMS_MAIN_INLINE_MARKUP
    else:
        # Незарегистрированный пользователь - показываем только кнопку регистрации
        from src.bot.structures.keyboards.dreams import REGISTRATION_REQUIRED_MARKUP
        reply_markup = REGISTRATION_REQUIRED_MARKUP

    if dream.image:
        await message.bot.send_photo(
            message.chat.id,
            types.BufferedInputFile(dream.image, filename=f"user_photo_{dream.id}.png"),
            caption=text,
            reply_markup=reply_markup,
            parse_mode='MARKDOWN'
        )
    else:
        await message.answer(text, reply_markup=reply_markup, parse_mode='MARKDOWN')


@dreams_router.message(F.text.lower().startswith('желания'))
@dreams_router.message(F.text == f"Желания {emoji.emojize(':thought_balloon:')}")
@dreams_router.message(Command(commands='dreams'))
async def process_dreams_handler(message: types.Message, state: FSMContext, db, redis_cache=None):
    user_id = message.from_user.id
    user = await db.user.user_register_check(active_user_id=user_id)

    if user:
        # Сбрасываем offset при начале нового просмотра желаний
        if redis_cache:
            await redis_cache.reset_user_offset(user_id)
            logging.info(f"User {user_id} dreams offset reset to 0")
        
        # Добавляем очки за просмотр желаний
        try:
            await db.progress.increment_dreams_viewed(user_id, 1)
        except Exception as e:
            logging.warning(f"Could not update dreams viewed for user {user_id}: {e}")
            # Продолжаем выполнение, даже если достижения не обновились
        
        # Получаем первое желание других пользователей (не свои)
        dream = await db.dream.get_dream_excluding_user(user_id=user_id, offset=0)
        logging.info(f"User {user_id} started viewing dreams, first dream: {dream.name if dream else 'None'}")
        await dreams_view_func(dream=dream, message=message, db=db, user=user)
    else:
        await state.set_state(RegisterGroup.age)
        register_text = (
            "🔒 **Регистрация обязательна** 🔒\n\n"
            "Для просмотра желаний нужно сначала зарегистрироваться в боте.\n\n"
            "**📝 Что нужно указать:**\n"
            "• Возраст\n"
            "• Пол\n"
            "• Город\n"
            "• Имя\n\n"
            "**🎯 После регистрации ты получишь:**\n"
            "• Доступ к просмотру желаний\n"
            "• Возможность создавать свои желания\n"
            "• Систему достижений и очков (+25 очков за регистрацию)\n"
            "• Категории желаний по интересам\n"
            "• Возможность зарабатывать очки за активность\n\n"
            "**🚀 Начнем регистрацию?**\n"
            "Сколько тебе лет? Просто введи число."
        )
        await message.answer(register_text, reply_markup=CANCEL_BUTTON, parse_mode="MARKDOWN")


async def send_notification_to_author(author_id, dream, message, redis_cache=None):
    """Отправляет группированное уведомление о лайках автору желания."""
    try:
        # Добавляем уведомление в очередь для группировки
        if redis_cache:
            liker_info = {
                "username": message.from_user.username,
                "user_id": message.from_user.id,
                "first_name": message.from_user.first_name
            }
            await redis_cache.add_like_notification(author_id, dream.id, liker_info)
            
            # Проверяем, есть ли уже ожидающие уведомления
            pending_notifications = await redis_cache.get_pending_like_notifications(author_id)
            
            # Если это первое уведомление, отправляем группированное сообщение
            if len(pending_notifications) == 1:
                await send_grouped_like_notification(author_id, dream, pending_notifications, message.bot, redis_cache)
        else:
            # Если Redis недоступен, отправляем обычное уведомление
            await send_single_like_notification(author_id, dream, message)

    except Exception as e:
        logging.error(f"Error sending notification: {e}")
        # Пытаемся отправить обычное уведомление как fallback
        try:
            await send_single_like_notification(author_id, dream, message)
        except Exception as fallback_error:
            logging.error(f"Fallback notification also failed: {fallback_error}")


async def send_grouped_like_notification(author_id, dream, notifications, bot, redis_cache=None):
    """Отправляет группированное уведомление о нескольких лайках."""
    try:
        if len(notifications) == 1:
            # Один лайк
            liker = notifications[0]["liker_info"]
            liker_name = liker.get("username", f"Пользователь {liker.get('first_name', 'Неизвестный')}")
            
            notification_message = (
                f"🎉 **Отличные новости!** 🎉\n\n"
                f"Твое желание **{dream.name}** получило лайк! ❤️\n\n"
                "**🏆 Достижения:**\n"
                "• +5 очков за получение лайка\n"
                "• Прогресс к достижению 'Популярный мечтатель'\n\n"
                f"**Кто заинтересовался:** {liker_name}\n\n"
                f"**🤔 Хочешь узнать, кто это?**\n"
                f"Можешь поделиться контактом для дальнейшего общения."
            )
        else:
            # Несколько лайков
            likers_info = []
            for notification in notifications:
                liker = notification["liker_info"]
                liker_name = liker.get("username", f"Пользователь {liker.get('first_name', 'Неизвестный')}")
                likers_info.append(f"• {liker_name}")
            
            notification_message = (
                f"🎉 **Отличные новости!** 🎉\n\n"
                f"Твое желание **{dream.name}** получило **{len(notifications)} лайков**! ❤️\n\n"
                "**🏆 Достижения:**\n"
                f"• +{len(notifications) * 5} очков за получение лайков\n"
                "• Прогресс к достижению 'Популярный мечтатель'\n\n"
                f"**Кто заинтересовался:**\n" + "\n".join(likers_info) + "\n\n"
                f"**🤔 Хочешь узнать, кто это?**\n"
                f"Можешь поделиться контактом для дальнейшего общения."
            )

        # Создаем кнопки для ответа
        # Для группированных уведомлений добавляем информацию о первом лайкнувшем
        first_liker = notifications[0]["liker_info"]
        liker_username = first_liker.get("username", str(first_liker.get("user_id", "unknown")))
        dream_username = dream.username or str(dream.user_id)
        # Используем user_id автора желания как chat_id, так как уведомление отправляется автору
        chat_id = str(dream.user_id)
        dream_id = str(dream.id)
        
        # Создаем callback данные с полной информацией
        callback_data = f"{liker_username} {dream_username} {chat_id} {dream_id}"
        
        reply_markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='Да, поделиться контактом', callback_data=f"share_contact_grouped {callback_data}"),
                    InlineKeyboardButton(text='Нет, спасибо', callback_data=f"not_share_contact_grouped {callback_data}")
                ]
            ]
        )

        await bot.send_message(
            author_id, 
            notification_message, 
            reply_markup=reply_markup,
            parse_mode='MARKDOWN'
        )

    except Exception as e:
        logging.error(f"Error sending grouped notification: {e}")
        # Пытаемся отправить обычное уведомление как fallback
        try:
            if len(notifications) > 0:
                first_notification = notifications[0]
                # Создаем mock message объект для fallback
                from aiogram.types import Message
                mock_message = type('MockMessage', (), {
                    'from_user': type('MockUser', (), {
                        'username': first_notification.get('liker_info', {}).get('username', 'unknown'),
                        'id': first_notification.get('liker_info', {}).get('user_id', 0),
                        'first_name': first_notification.get('liker_info', {}).get('first_name', 'Unknown')
                    })(),
                    'chat': type('MockChat', (), {'id': author_id})(),
                    'bot': bot
                })()
                await send_single_like_notification(author_id, dream, mock_message)
        except Exception as fallback_error:
            logging.error(f"Fallback notification also failed: {fallback_error}")


async def send_single_like_notification(author_id, dream, message):
    """Отправляет обычное уведомление о лайке (fallback)."""
    try:
        notification_message = (
            f"🎉 **Отличные новости!** 🎉\n\n"
            f"Твое желание **{dream.name}** получило лайк! ❤️\n\n"
            "**🏆 Достижения:**\n"
            "• +5 очков за получение лайка\n"
            "• Прогресс к достижению 'Популярный мечтатель'\n\n"
            f"Кто-то заинтересовался твоей мечтой и хочет помочь ей сбыться!\n\n"
            f"**🤔 Хочешь узнать, кто это?**\n"
            f"Можешь поделиться контактом для дальнейшего общения."
        )

        # Формируем callback данные с правильным количеством параметров
        liker_username = message.from_user.username or str(message.from_user.id)
        dream_username = dream.username or str(dream.user_id)
        chat_id = str(message.chat.id)
        dream_id = str(dream.id)
        
        # Создаем callback данные с пробелами между параметрами
        callback_data = f"{liker_username} {dream_username} {chat_id} {dream_id}"

        reply_markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='Да', callback_data=f"share_contact {callback_data}"),
                    InlineKeyboardButton(text='Нет', callback_data=f"not_share_contact {callback_data}")
                ]
            ]
        )

        await message.bot.send_message(
            author_id, 
            notification_message, 
            reply_markup=reply_markup,
            parse_mode='MARKDOWN'
        )

    except Exception as e:
        logging.error(f"Error sending single notification: {e}")
        # Пытаемся отправить простое уведомление без кнопок
        try:
            simple_message = f"🎉 Твое желание **{dream.name}** получило лайк! ❤️"
            await message.bot.send_message(author_id, simple_message, parse_mode='MARKDOWN')
        except Exception as simple_error:
            logging.error(f"Simple notification also failed: {simple_error}")


async def send_pending_notifications_periodically(bot, db, redis_cache):
    """Периодически отправляет группированные уведомления о лайках."""
    try:
        if not redis_cache:
            return
        
        # Получаем всех пользователей с ожидающими уведомлениями
        # Это можно оптимизировать, добавив список активных пользователей в Redis
        
        # Пока что просто логируем
        logging.info("Checking for pending notifications...")
        
    except Exception as e:
        logging.error(f"Error in periodic notification sender: {e}")


@dreams_router.callback_query(lambda c: c.data.startswith("share_contact") and not c.data.startswith("share_contact_grouped"))
async def share_contact_callback_handler(callback_query: CallbackQuery, db, redis_cache=None):
    try:
        data_parts = callback_query.data.split(' ')
        
        # Логируем для отладки
        logging.info(f"Share contact callback data: {callback_query.data}")
        logging.info(f"Data parts: {data_parts}")
        
        # Проверяем, что у нас достаточно данных для обычных уведомлений
        if len(data_parts) < 5:
            await callback_query.answer("Недостаточно данных для обработки")
            logging.error(f"Insufficient callback data: {callback_query.data}")
            return
        
        liker_username_id, dream_username_id, chat_id, dream_id = data_parts[1:5]
        
        # Логируем распарсенные данные
        logging.info(f"Parsed data: liker_username_id={liker_username_id}, dream_username_id={dream_username_id}, chat_id={chat_id}, dream_id={dream_id}")

        dream = await db.dream.get_dream_by_id(dream_id=dream_id)
        
        if not dream:
            await callback_query.answer("Желание не найдено")
            return

        notification_message = (
            f"Вот его профиль в Telegram, выполняйте "
            f"ваши совместные желания: {emoji.emojize(':smiling_face_with_hearts:')}\n"
            f"https://t.me/{liker_username_id}"
        )
        notification_for_sender_message = (
            f"Это автор желания *{dream.name}*, выполняйте совместные желания: "
            f"{emoji.emojize(':smiling_face_with_hearts:')}\n"
            f"https://t.me/{dream_username_id}"
        )
        
        # Логируем финальные сообщения
        logging.info(f"Notification message: {notification_message}")
        logging.info(f"Notification for sender: {notification_for_sender_message}")

        await callback_query.bot.send_message(chat_id, notification_for_sender_message,
                                              reply_markup=MENU_KEYBOARD, parse_mode='MARKDOWN')

        await callback_query.message.bot.edit_message_reply_markup(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            reply_markup=None
        )

        await db.dream_liked_record.new(
            author_user_id=dream_username_id,
            author_username=dream_username_id,
            liked_user_id=liker_username_id,
            liked_username=liker_username_id,
            dream_name=dream.name,
            type_feedback="share_contact"
        )

        await callback_query.message.answer(notification_message, reply_markup=MENU_KEYBOARD,
                                            parse_mode='MARKDOWN')
            
    except Exception as e:
        logging.error(f"Error in share_contact_callback_handler: {e}")
        await callback_query.answer("Произошла ошибка при обработке запроса")


@dreams_router.callback_query(lambda c: c.data.startswith("not_share_contact") and not c.data.startswith("not_share_contact_grouped"))
async def not_share_contact_callback_handler(callback_query: CallbackQuery, db, redis_cache=None):
    """Handle not share contact callback for single notifications."""
    try:
        data_parts = callback_query.data.split(' ')
        
        # Проверяем, что у нас достаточно данных для обычных уведомлений
        if len(data_parts) < 5:
            await callback_query.answer("Недостаточно данных для обработки")
            logging.error(f"Insufficient callback data: {callback_query.data}")
            return
        
        liker_username_id, dream_username_id, chat_id, dream_id = data_parts[1:5]
        
        await callback_query.answer("Контакт не будет передан")
        
        # Убираем кнопки из сообщения
        await callback_query.message.edit_reply_markup(reply_markup=None)
        
        # Показываем сообщение о том, что контакт не передан
        await callback_query.message.answer(
            "👍 **Понятно!** 👍\n\n"
            "Ты решил не делиться контактом. Это нормально!\n\n"
            "**💡 Что можно сделать:**\n"
            "• Продолжить просматривать желания\n"
            "• Создать свое желание\n"
            "• Настроить профиль\n\n"
            "Удачи в достижении твоих целей! 🚀",
            reply_markup=MENU_KEYBOARD,
            parse_mode="MARKDOWN"
        )
        
    except Exception as e:
        logging.error(f"Error in not_share_contact_callback_handler: {e}")
        await callback_query.answer("Произошла ошибка при обработке запроса")


@dreams_router.message(F.text.lower() == emoji.emojize(":red_heart:"))
async def process_like_command(message: types.Message, db, redis_cache=None):
    user_id = message.from_user.id
    
    # Проверяем, что это не бот
    if message.from_user.is_bot:
        logging.warning(f"Bot tried to like a dream, ignoring")
        return
    
    # Отладочная информация о состоянии базы данных
    await db.user.check_database_state()
    
    # Сначала проверяем, зарегистрирован ли пользователь
    user = await db.user.user_register_check(active_user_id=user_id)
    logging.info(f"User {user_id} registration check result: {user}")
    
    if not user:
        logging.warning(f"User {user_id} is not registered, showing registration message")
        # Показываем понятный интерфейс для регистрации
        from src.bot.structures.keyboards.dreams import REGISTRATION_REQUIRED_MARKUP
        
        await message.answer(
            "🔒 **Регистрация обязательна** 🔒\n\n"
            "Для постановки лайков нужно сначала зарегистрироваться в боте.\n\n"
            "**📝 Что дает регистрация:**\n"
            "• Возможность ставить лайки и дизлайки\n"
            "• Создание собственных желаний\n"
            "• Система достижений и очков\n"
            "• Доступ к категориям и статистике\n\n"
            "**🚀 Выберите действие:**",
            reply_markup=REGISTRATION_REQUIRED_MARKUP,
            parse_mode="MARKDOWN"
        )
        return
    
    logging.info(f"User {user_id} is registered, proceeding with like")
    
    # Используем Redis кэш для offset
    offset = await redis_cache.get_user_offset(user_id) if redis_cache else 0
    logging.info(f"User {user_id} liked dream at offset {offset}")
    
    # Получаем текущее желание других пользователей
    dream = await db.dream.get_dream_excluding_user(user_id=user_id, offset=offset)
    
    if not dream:
        await message.answer("Желание не найдено или больше нет доступных желаний")
        return
        
    author_id = dream.user_id if dream else None

    # Только зарегистрированные пользователи могут отправлять уведомления
    if author_id:
        # Создаем правильную структуру данных для уведомления
        liker_info = {
            "username": message.from_user.username,
            "user_id": message.from_user.id,
            "first_name": message.from_user.first_name
        }
        
        if redis_cache:
            # Добавляем уведомление в очередь для группировки
            await redis_cache.add_like_notification(author_id, dream.id, liker_info)
            
            # Проверяем, есть ли уже ожидающие уведомления
            pending_notifications = await redis_cache.get_pending_like_notifications(author_id)
            
            # Если это первое уведомление, отправляем группированное сообщение
            if len(pending_notifications) == 1:
                await send_grouped_like_notification(author_id, dream, pending_notifications, message.bot, redis_cache)
        else:
            # Если Redis недоступен, отправляем обычное уведомление
            await send_single_like_notification(author_id, dream, message)

    # Создаем запись о лайке
    if dream:  # Добавляем проверку
        try:
            await (
                db.dream_liked_record.new(
                    author_user_id=author_id,
                    liked_user_id=user_id,
                    liked_username=message.from_user.username,
                    dream_name=dream.name,
                    type_feedback="liked"
                ))
        except Exception as e:
            logging.error(f"Error creating like record: {e}")
    
    # Добавляем очки автору желания
    if author_id:
        try:
            await db.progress.increment_likes_received(author_id, 5)
            
            # Проверяем достижение "Популярный мечтатель" (25 лайков)
            author_progress = await db.progress.get_user_progress(author_id)
            if author_progress and author_progress.total_likes_received >= 25:
                if not await db.achievements.is_achievement_unlocked(author_id, "popular_dreamer"):
                    await db.achievements.unlock_achievement(author_id, "popular_dreamer", 75)
                    await db.progress.increment_likes_received(author_id, 75)  # Дополнительные очки за достижение
        except Exception as e:
            logging.warning(f"Could not update achievements for user {author_id}: {e}")
    
    # Добавляем очки тому, кто ставит лайк
    # Сначала проверяем, есть ли пользователь в базе
    user = await db.user.user_register_check(active_user_id=user_id)
    if not user:
        # Показываем понятный интерфейс для регистрации
        from src.bot.structures.keyboards.dreams import REGISTRATION_REQUIRED_MARKUP
        
        await message.answer(
            "🔒 **Регистрация обязательна** 🔒\n\n"
            "Для постановки лайков нужно сначала зарегистрироваться в боте.\n\n"
            "**📝 Что дает регистрация:**\n"
            "• Возможность ставить лайки и дизлайки\n"
            "• Создание собственных желаний\n"
            "• Система достижений и очков\n"
            "• Доступ к категориям и статистике\n\n"
            "**🚀 Выберите действие:**",
            reply_markup=REGISTRATION_REQUIRED_MARKUP,
            parse_mode="MARKDOWN"
        )
        return
    
    try:
        await db.progress.increment_likes_given(user_id, 2)
        
        # Проверяем достижение "Общительная бабочка" (100 лайков)
        user_progress = await db.progress.get_user_progress(user_id)
        if user_progress and user_progress.total_likes_given >= 100:
            if not await db.achievements.is_achievement_unlocked(user_id, "social_butterfly"):
                await db.achievements.unlock_achievement(user_id, "social_butterfly", 60)
                await db.progress.increment_likes_given(user_id, 60)  # Дополнительные очки за достижение
    except Exception as e:
        logging.warning(f"Could not update achievements for user {user_id}: {e}")

    # Увеличиваем offset для следующего желания
    if redis_cache:
        new_offset = await redis_cache.increment_user_offset(user_id)
        logging.info(f"User {user_id} offset incremented to {new_offset}")
        # Используем новый offset для получения следующего желания других пользователей
        next_dream = await db.dream.get_dream_excluding_user(user_id=user_id, offset=new_offset)
    else:
        # Если Redis недоступен, используем старый offset + 1
        next_dream = await db.dream.get_dream_excluding_user(user_id=user_id, offset=offset + 1)
    
    # Если следующее желание не найдено, показываем сообщение
    if not next_dream:
        no_more_dreams_text = (
            "😔 **Больше желаний не найдено** 😔\n\n"
            "Похоже, ты просмотрел все доступные желания в данный момент.\n\n"
            "**💡 Что можно сделать:**\n"
            "• Создать свое желание (+15 очков)\n"
            "• Вернуться в главное меню\n\n"
            "**🌟 Совет:** Возможно, стоит создать свое желание и вдохновить других! Это принесет тебе очки и поможет разблокировать достижения!"
        )
        from src.bot.structures.keyboards.dreams import DREAMS_NOT_FOUND_INLINE_MARKUP
        
        # Редактируем существующее сообщение вместо создания нового
        try:
            await message.edit_text(
                no_more_dreams_text,
                reply_markup=DREAMS_NOT_FOUND_INLINE_MARKUP,
                parse_mode="MARKDOWN"
            )
        except Exception as e:
            logging.warning(f"Could not edit message, sending new one: {e}")
            await message.answer(no_more_dreams_text, reply_markup=DREAMS_NOT_FOUND_INLINE_MARKUP, parse_mode="MARKDOWN")
        return
    
    # Редактируем существующее сообщение, заменяя старое желание на новое
    try:
        await edit_message_with_dream(message, next_dream, db, user)
    except Exception as e:
        logging.warning(f"Could not edit message, sending new one: {e}")
        await dreams_view_func(dream=next_dream, message=message, db=db, user=user)


@dreams_router.message(F.text.lower() == emoji.emojize(":thumbs_down:"))
async def process_dislike_command(message: types.Message, db, redis_cache=None):
    user_id = message.from_user.id
    
    # Проверяем, что это не бот
    if message.from_user.is_bot:
        logging.warning(f"Bot tried to dislike a dream, ignoring")
        return
    
    # Сначала проверяем, зарегистрирован ли пользователь
    user = await db.user.user_register_check(active_user_id=user_id)
    if not user:
        # Показываем понятный интерфейс для регистрации
        from src.bot.structures.keyboards.dreams import REGISTRATION_REQUIRED_MARKUP
        
        await message.answer(
            "🔒 **Регистрация обязательна** 🔒\n\n"
            "Для постановки дизлайков нужно сначала зарегистрироваться в боте.\n\n"
            "**📝 Что дает регистрация:**\n"
            "• Возможность ставить лайки и дизлайки\n"
            "• Создание собственных желаний\n"
            "• Система достижений и очков\n"
            "• Доступ к категориям и статистике\n\n"
            "**🚀 Выберите действие:**",
            reply_markup=REGISTRATION_REQUIRED_MARKUP,
            parse_mode="MARKDOWN"
        )
        return
    
    # Используем Redis кэш для offset
    offset = await redis_cache.get_user_offset(user_id) if redis_cache else 0
    logging.info(f"User {user_id} disliked dream at offset {offset}")
    
    # Получаем текущее желание других пользователей
    dream = await db.dream.get_dream_excluding_user(user_id=user_id, offset=offset)
    
    if not dream:
        await message.answer("Желание не найдено или больше нет доступных желаний")
        return
    
    # Проверяем, зарегистрирован ли пользователь
    user = await db.user.user_register_check(active_user_id=user_id)
    if not user:
        # Показываем понятный интерфейс для регистрации
        from src.bot.structures.keyboards.dreams import REGISTRATION_REQUIRED_MARKUP
        
        await message.answer(
            "🔒 **Регистрация обязательна** 🔒\n\n"
            "Для постановки дизлайков нужно сначала зарегистрироваться в боте.\n\n"
            "**📝 Что дает регистрация:**\n"
            "• Возможность ставить лайки и дизлайки\n"
            "• Создание собственных желаний\n"
            "• Система достижений и очков\n"
            "• Доступ к категориям и статистике\n\n"
            "**🚀 Выберите действие:**",
            reply_markup=REGISTRATION_REQUIRED_MARKUP,
            parse_mode="MARKDOWN"
        )
        return
    
    # Увеличиваем offset для следующего желания
    if redis_cache:
        new_offset = await redis_cache.increment_user_offset(user_id)
        logging.info(f"User {user_id} offset incremented to {new_offset}")
        # Используем новый offset для получения следующего желания других пользователей
        next_dream = await db.dream.get_dream_excluding_user(user_id=user_id, offset=new_offset)
    else:
        # Если Redis недоступен, используем старый offset + 1
        next_dream = await db.dream.get_dream_excluding_user(user_id=user_id, offset=offset + 1)
    
    # Если следующее желание не найдено, показываем сообщение
    if not next_dream:
        no_more_dreams_text = (
            "😔 **Больше желаний не найдено** 😔\n\n"
            "Похоже, ты просмотрел все доступные желания в данный момент.\n\n"
            "**💡 Что можно сделать:**\n"
            "• Создать свое желание (+15 очков)\n"
            "• Вернуться в главное меню\n\n"
            "**🌟 Совет:** Возможно, стоит создать свое желание и вдохновить других! Это принесет тебе очки и поможет разблокировать достижения!"
        )
        from src.bot.structures.keyboards.dreams import DREAMS_NOT_FOUND_INLINE_MARKUP
        
        # Редактируем существующее сообщение вместо создания нового
        try:
            await message.edit_text(
                no_more_dreams_text,
                reply_markup=DREAMS_NOT_FOUND_INLINE_MARKUP,
                parse_mode="MARKDOWN"
            )
        except Exception as e:
            logging.warning(f"Could not edit message, sending new one: {e}")
            await message.answer(no_more_dreams_text, reply_markup=DREAMS_NOT_FOUND_INLINE_MARKUP, parse_mode="MARKDOWN")
        return
    
    # Редактируем существующее сообщение, заменяя старое желание на новое
    try:
        await edit_message_with_dream(message, next_dream, db, user)
    except Exception as e:
        logging.warning(f"Could not edit message, sending new one: {e}")
        await dreams_view_func(dream=next_dream, message=message, db=db, user=user)


@dreams_router.message(F.text.lower() == emoji.emojize(":ZZZ:"))
async def process_sleep_command(message: types.Message, db):
    user = await db.user.user_register_check(active_user_id=message.from_user.id)

    user_name = user.name or message.from_user.first_name
    message_text = (
        f"😴 **Привет, {user_name}!** 😴\n\n"
        "Видимо, ты устал от просмотра желаний. Отдохни немного!\n\n"
        "**💤 Что можно сделать:**\n"
        "• Просмотреть новые желания\n"
        "• Управлять своими желаниями\n"
        "• Изменить профиль\n"
        "• Вернуться в главное меню\n\n"
        "**💡 Совет:** Возможно, стоит попробовать другой подход - создай свое желание!"
    )

    await message.answer(message_text, reply_markup=MENU_KEYBOARD, parse_mode="MARKDOWN")


@dreams_router.message(F.text.lower() == "🔄 начать сначала")
async def process_restart_command(message: types.Message, db, redis_cache=None):
    user_id = message.from_user.id
    user = await db.user.user_register_check(active_user_id=user_id)

    if user:
        # Сбрасываем offset и начинаем сначала
        if redis_cache:
            await redis_cache.reset_user_offset(user_id)
        
        restart_text = (
            "🔄 **Начинаем сначала!** 🔄\n\n"
            "Отлично! Теперь ты снова будешь видеть все желания с самого начала.\n\n"
            "**💡 Что изменилось:**\n"
            "• Счетчик просмотров сброшен\n"
            "• Показываем первое желание\n"
            "• Можешь заново оценить все желания\n\n"
            "**🚀 Начинаем просмотр:**"
        )
        
        # Получаем первое желание
        dream = await db.dream.get_dream(user_id=user_id, offset=0)
        await message.answer(restart_text, parse_mode="MARKDOWN")
        await dreams_view_func(dream=dream, message=message, db=db, user=user)
    else:
        await message.answer(
            "🔒 **Регистрация обязательна** 🔒\n\n"
            "Для просмотра желаний нужно сначала зарегистрироваться.",
            reply_markup=MENU_KEYBOARD,
            parse_mode="MARKDOWN"
        )

# Обработчик для выбора категории при создании желания
@dreams_router.callback_query(lambda c: c.data.startswith("cat_"))
async def category_selection_callback(callback_query: types.CallbackQuery, state: FSMContext):
    """Handle category selection during dream creation."""
    category_id = callback_query.data.replace("cat_", "")
    
    # Получаем информацию о категории
    from src.bot.structures.dream_categories import category_system
    category = category_system.get_category(category_id)
    
    if not category:
        await callback_query.answer("Категория не найдена")
        return
    
    # Сохраняем выбранную категорию
    await state.update_data(category=category.name)
    await state.set_state(DreamGroup.description)
    
    await callback_query.answer(f"Выбрана категория: {category.name}")
    
    # Показываем следующий шаг
    description_text = (
        f"📝 **Шаг 3 из 5: Описание** 📝\n\n"
        f"Отлично! Категория **{category.name}** выбрана.\n\n"
        "Теперь расскажи подробнее о своем желании.\n\n"
        "**💭 Что написать:**\n"
        "• Почему это важно для тебя\n"
        "• Что именно ты хочешь\n"
        "• Когда и где это можно реализовать\n"
        "• Какая помощь нужна\n\n"
        "**💡 Пример:**\n"
        "Хочу научиться играть на гитаре. Ищу учителя или единомышленника для совместных занятий. "
        "Могу заниматься по вечерам в центре города. Готов оплатить уроки или обменяться навыками."
    )

    await callback_query.message.answer(
        description_text, 
        reply_markup=CANCEL_BUTTON, 
        parse_mode="MARKDOWN"
    )


@dreams_router.callback_query(lambda c: c.data.startswith("share_contact_grouped"))
async def share_contact_grouped_callback_handler(callback_query: CallbackQuery, db, redis_cache=None):
    """Handle grouped share contact callback."""
    try:
        # Парсим callback данные: "share_contact_grouped {liker_username} {dream_username} {chat_id} {dream_id}"
        data_parts = callback_query.data.split(' ')
        if len(data_parts) < 5:
            await callback_query.answer("Недостаточно данных для обработки")
            return
            
        liker_username_id, dream_username_id, chat_id, dream_id = data_parts[1:5]
        dream = await db.dream.get_dream_by_id(dream_id=dream_id)
        
        if not dream:
            await callback_query.answer("Желание не найдено")
            return
        
        # Получаем все ожидающие уведомления для этого желания
        if not redis_cache:
            await callback_query.answer("Redis недоступен")
            return
            
        pending_notifications = await redis_cache.get_pending_like_notifications(dream.user_id)
        
        if not pending_notifications:
            await callback_query.answer("Нет активных уведомлений")
            return
        
        # Отправляем информацию о всех лайкнувших
        likers_info = []
        for notification in pending_notifications:
            liker = notification["liker_info"]
            if liker["username"]:
                likers_info.append(f"• @{liker['username']} ({liker['first_name']})")
            else:
                likers_info.append(f"• Пользователь {liker['first_name']} (ID: {liker['user_id']})")
        
        # Уведомление для автора
        notification_message = (
            f"🌟 **Вот кто заинтересовался твоим желанием!** 🌟\n\n"
            f"**Желание:** {dream.name}\n"
            f"**Количество лайков:** {len(pending_notifications)}\n\n"
            "**Лайкнувшие пользователи:**\n" + "\n".join(likers_info) + "\n\n"
            "**💡 Что дальше?**\n"
            "• Напиши им в личные сообщения\n"
            "• Обсудите детали реализации\n"
            "• Вместе воплотите мечту в жизнь!"
        )
        
        await callback_query.message.edit_text(
            notification_message,
            parse_mode="MARKDOWN"
        )
        
        # Очищаем уведомления
        await redis_cache.clear_like_notifications(dream.user_id)
        
        await callback_query.answer("Контакты отправлены!")
        
    except Exception as e:
        logging.error(f"Error in grouped share contact handler: {e}")
        await callback_query.answer("Произошла ошибка")


@dreams_router.callback_query(lambda c: c.data.startswith("not_share_contact_grouped"))
async def not_share_contact_grouped_callback_handler(callback_query: CallbackQuery, db, redis_cache=None):
    """Handle grouped not share contact callback."""
    try:
        # Парсим callback данные: "not_share_contact_grouped {liker_username} {dream_username} {chat_id} {dream_id}"
        data_parts = callback_query.data.split(' ')
        if len(data_parts) < 5:
            await callback_query.answer("Недостаточно данных для обработки")
            return
            
        liker_username_id, dream_username_id, chat_id, dream_id = data_parts[1:5]
        dream = await db.dream.get_dream_by_id(dream_id=dream_id)
        
        if not dream:
            await callback_query.answer("Желание не найдено")
            return
        
        # Просто очищаем уведомления
        if redis_cache:
            await redis_cache.clear_like_notifications(dream.user_id)
        
        await callback_query.message.edit_text(
            "👍 **Понятно!** 👍\n\n"
            "Ты решил не делиться контактом. Это нормально!\n\n"
            "**💡 Что можно сделать:**\n"
            "• Продолжить просматривать желания\n"
            "• Создать свое желание\n"
            "• Настроить профиль\n\n"
            "Удачи в достижении твоих целей! 🚀",
            parse_mode="MARKDOWN"
        )
        
        await callback_query.answer("Уведомления очищены!")
        
    except Exception as e:
        logging.error(f"Error in grouped not share contact handler: {e}")
        await callback_query.answer("Произошла ошибка")


@dreams_router.callback_query(lambda c: c.data == "like_dream")
async def like_dream_callback_handler(callback_query: CallbackQuery, db, redis_cache=None):
    """Handle like dream button press."""
    try:
        user_id = callback_query.from_user.id
        
        # Проверяем, что это не бот
        if callback_query.from_user.is_bot:
            logging.warning(f"Bot tried to like a dream via callback, ignoring")
            await callback_query.answer("Ошибка: бот не может ставить лайки")
            return
        
        # Сначала проверяем, зарегистрирован ли пользователь
        user = await db.user.user_register_check(active_user_id=user_id)
        if not user:
            # Пытаемся убрать кнопки лайк/дизлайк из сообщения
            try:
                await callback_query.message.edit_reply_markup(reply_markup=None)
            except Exception:
                # Если не удалось отредактировать, просто логируем
                logging.info(f"Could not edit reply markup for user {user_id}")
            
            # Показываем понятный интерфейс для регистрации
            from src.bot.structures.keyboards.dreams import REGISTRATION_REQUIRED_MARKUP
            
            await callback_query.message.answer(
                "🔒 **Регистрация обязательна** 🔒\n\n"
                "Для постановки лайков нужно сначала зарегистрироваться в боте.\n\n"
                "**📝 Что дает регистрация:**\n"
                "• Возможность ставить лайки и дизлайки\n"
                "• Создание собственных желаний\n"
                "• Система достижений и очков\n"
                "• Доступ к категориям и статистике\n\n"
                "**🚀 Выберите действие:**",
                reply_markup=REGISTRATION_REQUIRED_MARKUP,
                parse_mode="MARKDOWN"
            )
            await callback_query.answer("Требуется регистрация")
            return
        
        # Получаем текущее желание других пользователей из offset
        offset = await redis_cache.get_user_offset(user_id) if redis_cache else 0
        dream = await db.dream.get_dream_excluding_user(user_id=user_id, offset=offset)
        
        if not dream:
            await callback_query.answer("Желание не найдено или больше нет доступных желаний")
            return
        
        # Обрабатываем лайк напрямую
        author_id = dream.user_id if dream else None
        
        # Создаем запись о лайке
        if dream:
            try:
                await (
                    db.dream_liked_record.new(
                        author_user_id=author_id,
                        liked_user_id=user_id,
                        liked_username=callback_query.from_user.username,
                        dream_name=dream.name,
                        type_feedback="liked"
                    ))
            except Exception as e:
                logging.error(f"Error creating like record: {e}")
        
        # Добавляем очки автору желания
        if author_id:
            try:
                await db.progress.increment_likes_received(author_id, 5)
                
                # Проверяем достижение "Популярный мечтатель" (25 лайков)
                author_progress = await db.progress.get_user_progress(author_id)
                if author_progress and author_progress.total_likes_received >= 25:
                    if not await db.achievements.is_achievement_unlocked(author_id, "popular_dreamer"):
                        await db.achievements.unlock_achievement(author_id, "popular_dreamer", 75)
                        await db.progress.increment_likes_received(author_id, 75)  # Дополнительные очки за достижение
            except Exception as e:
                logging.warning(f"Could not update achievements for user {author_id}: {e}")
        
        # Добавляем очки тому, кто ставит лайк
        try:
            await db.progress.increment_likes_given(user_id, 2)
            
            # Проверяем достижение "Общительная бабочка" (100 лайков)
            user_progress = await db.progress.get_user_progress(user_id)
            if user_progress and user_progress.total_likes_given >= 100:
                if not await db.achievements.is_achievement_unlocked(user_id, "social_butterfly"):
                    await db.achievements.unlock_achievement(user_id, "social_butterfly", 60)
                    await db.progress.increment_likes_given(user_id, 60)  # Дополнительные очки за достижение
        except Exception as e:
            logging.warning(f"Could not update achievements for user {user_id}: {e}")
        
        # Отправляем уведомление автору (для дизлайка это может быть не нужно, но оставляем для консистентности)
        if author_id:
            # Создаем правильную структуру данных для уведомления
            liker_info = {
                "username": callback_query.from_user.username,
                "user_id": callback_query.from_user.id,
                "first_name": callback_query.from_user.first_name
            }
            
            if redis_cache:
                # Добавляем уведомление в очередь для группировки
                await redis_cache.add_like_notification(author_id, dream.id, liker_info)
                
                # Проверяем, есть ли уже ожидающие уведомления
                pending_notifications = await redis_cache.get_pending_like_notifications(author_id)
                
                # Если это первое уведомление, отправляем группированное сообщение
                if len(pending_notifications) == 1:
                    await send_grouped_like_notification(author_id, dream, pending_notifications, callback_query.bot, redis_cache)
            else:
                # Если Redis недоступен, отправляем обычное уведомление
                await send_single_like_notification(author_id, dream, callback_query)
        
        # Увеличиваем offset для следующего желания
        if redis_cache:
            new_offset = await redis_cache.increment_user_offset(user_id)
            logging.info(f"User {user_id} offset incremented to {new_offset}")
            # Используем новый offset для получения следующего желания других пользователей
            next_dream = await db.dream.get_dream_excluding_user(user_id=user_id, offset=new_offset)
        else:
            # Если Redis недоступен, используем старый offset + 1
            next_dream = await db.dream.get_dream_excluding_user(user_id=user_id, offset=offset + 1)
        
        # Если следующее желание не найдено, показываем сообщение
        if not next_dream:
            no_more_dreams_text = (
                "😔 **Больше желаний не найдено** 😔\n\n"
                "Похоже, ты просмотрел все доступные желания в данный момент.\n\n"
                "**💡 Что можно сделать:**\n"
                "• Создать свое желание (+15 очков)\n"
                "• Вернуться в главное меню\n\n"
                "**🌟 Совет:** Возможно, стоит создать свое желание и вдохновить других! Это принесет тебе очки и поможет разблокировать достижения!"
            )
            from src.bot.structures.keyboards.dreams import DREAMS_NOT_FOUND_INLINE_MARKUP
            
            # Редактируем существующее сообщение вместо создания нового
            try:
                await callback_query.message.edit_text(
                    no_more_dreams_text,
                    reply_markup=DREAMS_NOT_FOUND_INLINE_MARKUP,
                    parse_mode="MARKDOWN"
                )
            except Exception as e:
                logging.warning(f"Could not edit message, sending new one: {e}")
                await callback_query.message.answer(no_more_dreams_text, reply_markup=DREAMS_NOT_FOUND_INLINE_MARKUP, parse_mode="MARKDOWN")
            return
        
        # Редактируем существующее сообщение, заменяя старое желание на новое
        try:
            await edit_message_with_dream(callback_query.message, next_dream, db, user)
        except Exception as e:
            logging.warning(f"Could not edit message, sending new one: {e}")
            await dreams_view_func(dream=next_dream, message=callback_query.message, db=db, user=user)
        
        # Убираем удаление inline кнопок, так как edit_message_with_dream уже добавляет правильные
        # await callback_query.message.edit_reply_markup(reply_markup=None)
        
        await callback_query.answer("Лайк поставлен! ❤️")
        
    except Exception as e:
        logging.error(f"Error in like dream callback: {e}")
        await callback_query.answer("Произошла ошибка")


@dreams_router.callback_query(lambda c: c.data == "dislike_dream")
async def dislike_dream_callback_handler(callback_query: CallbackQuery, db, redis_cache=None):
    """Handle dislike dream button press."""
    try:
        user_id = callback_query.from_user.id
        
        # Проверяем, что это не бот
        if callback_query.from_user.is_bot:
            logging.warning(f"Bot tried to dislike a dream via callback, ignoring")
            await callback_query.answer("Ошибка: бот не может ставить дизлайки")
            return
        
        # Сначала проверяем, зарегистрирован ли пользователь
        user = await db.user.user_register_check(active_user_id=user_id)
        if not user:
            # Пытаемся убрать кнопки лайк/дизлайк из сообщения
            try:
                await callback_query.message.edit_reply_markup(reply_markup=None)
            except Exception:
                # Если не удалось отредактировать, просто логируем
                logging.info(f"Could not edit reply markup for user {user_id}")
            
            # Показываем понятный интерфейс для регистрации
            from src.bot.structures.keyboards.dreams import REGISTRATION_REQUIRED_MARKUP
            
            await callback_query.message.answer(
                "🔒 **Регистрация обязательна** 🔒\n\n"
                "Для постановки дизлайков нужно сначала зарегистрироваться в боте.\n\n"
                "**📝 Что дает регистрация:**\n"
                "• Возможность ставить лайки и дизлайки\n"
                "• Создание собственных желаний\n"
                "• Система достижений и очков\n"
                "• Доступ к категориям и статистике\n\n"
                "**🚀 Выберите действие:**",
                reply_markup=REGISTRATION_REQUIRED_MARKUP,
                parse_mode="MARKDOWN"
            )
            await callback_query.answer("Требуется регистрация")
            return
        
        # Получаем текущее желание других пользователей из offset
        offset = await redis_cache.get_user_offset(user_id) if redis_cache else 0
        dream = await db.dream.get_dream_excluding_user(user_id=user_id, offset=offset)
        
        if not dream:
            await callback_query.answer("Желание не найдено или больше нет доступных желаний")
            return
        
        # Обрабатываем дизлайк напрямую
        author_id = dream.user_id if dream else None
        
        # Создаем запись о дизлайке
        if dream:
            try:
                await (
                    db.dream_liked_record.new(
                        author_user_id=author_id,
                        liked_user_id=user_id,
                        liked_username=callback_query.from_user.username,
                        dream_name=dream.name,
                        type_feedback="disliked"
                    ))
            except Exception as e:
                logging.error(f"Error creating dislike record: {e}")
        
        # Увеличиваем offset для следующего желания
        if redis_cache:
            new_offset = await redis_cache.increment_user_offset(user_id)
            logging.info(f"User {user_id} offset incremented to {new_offset}")
            # Используем новый offset для получения следующего желания других пользователей
            next_dream = await db.dream.get_dream_excluding_user(user_id=user_id, offset=new_offset)
        else:
            # Если Redis недоступен, используем старый offset + 1
            next_dream = await db.dream.get_dream_excluding_user(user_id=user_id, offset=offset + 1)
        
        # Если следующее желание не найдено, показываем сообщение
        if not next_dream:
            no_more_dreams_text = (
                "😔 **Больше желаний не найдено** 😔\n\n"
                "Похоже, ты просмотрел все доступные желания в данный момент.\n\n"
                "**💡 Что можно сделать:**\n"
                "• Создать свое желание (+15 очков)\n"
                "• Вернуться в главное меню\n\n"
                "**🌟 Совет:** Возможно, стоит создать свое желание и вдохновить других! Это принесет тебе очки и поможет разблокировать достижения!"
            )
            from src.bot.structures.keyboards.dreams import DREAMS_NOT_FOUND_INLINE_MARKUP
            
            # Редактируем существующее сообщение вместо создания нового
            try:
                await callback_query.message.edit_text(
                    no_more_dreams_text,
                    reply_markup=DREAMS_NOT_FOUND_INLINE_MARKUP,
                    parse_mode="MARKDOWN"
                )
            except Exception as e:
                logging.warning(f"Could not edit message, sending new one: {e}")
                await callback_query.message.answer(no_more_dreams_text, reply_markup=DREAMS_NOT_FOUND_INLINE_MARKUP, parse_mode="MARKDOWN")
            return
        
        # Редактируем существующее сообщение, заменяя старое желание на новое
        try:
            await edit_message_with_dream(callback_query.message, next_dream, db, user)
        except Exception as e:
            logging.warning(f"Could not edit message, sending new one: {e}")
            await dreams_view_func(dream=next_dream, message=callback_query.message, db=db, user=user)
        
        # Убираем удаление inline кнопок, так как edit_message_with_dream уже добавляет правильные
        # await callback_query.message.edit_reply_markup(reply_markup=None)
        
        await callback_query.answer("Дизлайк поставлен! 👎")
        
    except Exception as e:
        logging.error(f"Error in dislike dream callback: {e}")
        await callback_query.answer("Произошла ошибка")


@dreams_router.callback_query(lambda c: c.data == "main_menu")
async def main_menu_callback_handler(callback_query: CallbackQuery, db, redis_cache=None):
    """Handle main menu button press."""
    try:
        from src.bot.structures.keyboards.menu import MENU_KEYBOARD
        
        await callback_query.message.answer(
            "🏠 **Главное меню** 🏠\n\n"
            "Выберите действие:",
            reply_markup=MENU_KEYBOARD,
            parse_mode="MARKDOWN"
        )
        await callback_query.answer("Главное меню открыто! 🏠")
        
    except Exception as e:
        logging.error(f"Error in main menu callback: {e}")
        await callback_query.answer("Произошла ошибка")


@dreams_router.callback_query(lambda c: c.data == "create_dream")
async def create_dream_callback_handler(callback_query: CallbackQuery, state: FSMContext, db, redis_cache=None):
    """Handle create dream button press."""
    try:
        from src.bot.structures.fsm.dream_create import DreamGroup
        
        # Проверяем, зарегистрирован ли пользователь
        user = await db.user.user_register_check(active_user_id=callback_query.from_user.id)
        if not user:
            await callback_query.answer("Сначала нужно зарегистрироваться! 🔒")
            await callback_query.message.answer(
                "🔒 **Регистрация обязательна** 🔒\n\n"
                "Для создания желаний нужно сначала зарегистрироваться в боте.\n\n"
                "**💡 Что дает регистрация:**\n"
                "• Возможность создавать желания\n"
                "• Система достижений и очков\n"
                "• Доступ к категориям\n\n"
                "**🚀 Начни регистрацию прямо сейчас!**",
                reply_markup=REGISTRATION_REQUIRED_MARKUP,
                parse_mode="MARKDOWN"
            )
            return
        
        # Устанавливаем состояние создания желания
        await state.set_state(DreamGroup.name)
        
        await callback_query.message.answer(
            "💭 **Создание нового желания** 💭\n\n"
            "Давайте создадим твое желание! Это займет всего несколько шагов.\n\n"
            "**Шаг 1/5: Название**\n"
            "Напиши название своего желания:",
            reply_markup=CANCEL_BUTTON,
            parse_mode="MARKDOWN"
        )
        
        await callback_query.answer("Начинаем создание желания! 💭")
        
    except Exception as e:
        logging.error(f"Error in create dream callback: {e}")
        await callback_query.answer("Произошла ошибка")
        # Fallback - показываем инструкции
        await callback_query.message.answer(
            "**💡 Для создания желания используй главное меню**",
            parse_mode="MARKDOWN"
        )


@dreams_router.callback_query(lambda c: c.data == "retry_dreams")
async def retry_dreams_callback_handler(callback_query: CallbackQuery, db, redis_cache=None):
    """Handle retry dreams button press."""
    try:
        user_id = callback_query.from_user.id
        
        # Сбрасываем offset и показываем первое желание
        if redis_cache:
            await redis_cache.set_user_offset(user_id, 0)
        
        dream = await db.dream.get_dream(user_id=user_id, offset=0)
        await dreams_view_func(dream=dream, message=callback_query.message, db=db, user=await db.user.user_register_check(active_user_id=user_id))
        
        await callback_query.answer("Начинаем сначала! 🔄")
        
    except Exception as e:
        logging.error(f"Error in retry dreams callback: {e}")
        await callback_query.answer("Произошла ошибка")


@dreams_router.callback_query(lambda c: c.data == "start_registration")
async def start_registration_callback_handler(callback_query: CallbackQuery, state: FSMContext, db, redis_cache=None):
    """Handle start registration button press."""
    try:
        from src.bot.structures.fsm.register import RegisterGroup
        
        user_id = callback_query.from_user.id
        logging.info(f"Start registration callback for user {user_id}")
        
        # Проверяем, не зарегистрирован ли уже пользователь
        existing_user = await db.user.user_register_check(active_user_id=user_id)
        logging.info(f"User {user_id} registration check result: {existing_user}")
        
        if existing_user:
            logging.info(f"User {user_id} is already registered, showing main menu")
            await callback_query.answer("Ты уже зарегистрирован! 🎉")
            await callback_query.message.answer(
                f"🤔 **Ты уже зарегистрирован!** 🤔\n\n"
                f"Привет, **{existing_user.name or 'Пользователь'}**! 👋\n\n"
                "**💡 Что можно сделать:**\n"
                "• Просматривать желания других пользователей\n"
                "• Создавать свои желания\n"
                "• Изучать категории и достижения\n"
                "• Находить единомышленников\n\n"
                "**🚀 Начни прямо сейчас!**",
                reply_markup=MENU_KEYBOARD,
                parse_mode="MARKDOWN"
            )
            return
        
        logging.info(f"User {user_id} is not registered, starting registration")
        
        # Устанавливаем состояние регистрации
        await state.set_state(RegisterGroup.age)
        
        # Показываем первый шаг регистрации
        await callback_query.message.answer(
            "🎉 **Отлично! Начинаем регистрацию!** 🎉\n\n"
            "Давай познакомимся поближе! Это займет всего несколько минут.\n\n"
            "**Шаг 1 из 5: Возраст** 📅\n"
            "Сколько тебе лет? Просто введи число.",
            reply_markup=CANCEL_BUTTON,
            parse_mode="MARKDOWN"
        )
        
        await callback_query.answer("Регистрация начата! 🚀")
        
    except Exception as e:
        logging.error(f"Error in start registration callback: {e}")
        await callback_query.answer("Произошла ошибка")
        # Fallback - показываем инструкции
        await callback_query.message.answer(
            "**💡 Для продолжения регистрации нажми /start**",
            parse_mode="MARKDOWN"
        )


@dreams_router.callback_query(lambda c: c.data == "how_it_works")
async def how_it_works_callback_handler(callback_query: CallbackQuery, db, redis_cache=None):
    """Handle how it works button press."""
    try:
        await callback_query.message.answer(
            "❓ **Как работает Wanty?** ❓\n\n"
            "**🎯 Основная идея:**\n"
            "Wanty - это платформа для поиска единомышленников и воплощения желаний в жизнь!\n\n"
            "**📱 Что можно делать:**\n"
            "• Просматривать желания других пользователей\n"
            "• Ставить лайки понравившимся идеям\n"
            "• Создавать свои желания\n"
            "• Находить людей с похожими целями\n"
            "• Зарабатывать очки и достижения\n\n"
            "**🏆 Система достижений:**\n"
            "• Создание желания: +15 очков\n"
            "• Получение лайка: +5 очков\n"
            "• Просмотр желаний: +1 очко\n"
            "• Регистрация: +25 очков\n\n"
            "**🚀 Начни прямо сейчас!**\n"
            "Нажми '🚀 Начать регистрацию' для старта!",
            parse_mode="MARKDOWN"
        )
        
        await callback_query.answer("Информация показана! ❓")
        
    except Exception as e:
        logging.error(f"Error in how it works callback: {e}")
        await callback_query.answer("Произошла ошибка")


@dreams_router.callback_query(lambda c: c.data == "create_without_image")
async def create_without_image_handler(callback_query: CallbackQuery, state: FSMContext, db, redis_cache=None):
    """Handle create dream without image button press."""
    try:
        data = await state.get_data()
        description = data.get('description', '')
        category = data.get('category', '')

        # Создаем желание без изображения
        await db.dream.new(
            user_id=callback_query.from_user.id,
            username=callback_query.from_user.username,
            image=None,
            name=data.get('name', ''),
            description=description,
            category=category
        )
        
        # Добавляем очки и проверяем достижения
        try:
            await db.progress.increment_dreams(callback_query.from_user.id, 15)
            
            # Проверяем, нужно ли разблокировать достижение "Первый шаг"
            if not await db.achievements.is_achievement_unlocked(callback_query.from_user.id, "first_dream"):
                await db.achievements.unlock_achievement(callback_query.from_user.id, "first_dream", 10)
                await db.progress.increment_dreams(callback_query.from_user.id, 10)  # Дополнительные очки за достижение
        except Exception as e:
            logging.warning(f"Could not update achievements for user {callback_query.from_user.id}: {e}")
            # Продолжаем выполнение, даже если достижения не обновились
        
        await state.clear()
        success_text = (
            "🎉 **Желание успешно создано!** 🎉\n\n"
            f"**📂 Категория:** {category}\n\n"
            "Поздравляем! Твое желание теперь доступно всем пользователям Wanty.\n\n"
            "**🏆 Достижения:**\n"
            "• +15 очков за создание желания\n"
            "• Возможно, ты разблокировал новое достижение!\n\n"
            "**✨ Что дальше?**\n"
            "• Жди откликов от единомышленников\n"
            "• Получай уведомления о лайках\n"
            "• Создавай новые желания\n"
            "• Просматривай желания других\n\n"
            "**💡 Совет:** Будь активным! Чем больше ты взаимодействуешь с другими, тем больше шансов найти единомышленников и получить достижения!"
        )
        
        await callback_query.message.edit_text(
            success_text,
            reply_markup=DREAMS_NOT_FOUND_INLINE_MARKUP,
            parse_mode="MARKDOWN"
        )
        
        await callback_query.answer("Желание создано без изображения! 🎉")
        
    except Exception as e:
        logging.error(f"Error creating dream without image: {e}")
        await callback_query.answer("Произошла ошибка при создании желания")
