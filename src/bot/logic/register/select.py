"""This file represents a Register logic."""
import emoji
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from .router import register_router
from src.bot.structures.fsm.register import RegisterGroup
from src.bot.structures.keyboards.register import REGISTER_USER_COUNTRY, REGISTER_USER_GENDER, REGISTER_SUCCESS_MARKUP, \
    REGISTER_START_CONFIRM
from src.bot.structures.keyboards.menu import MENU_KEYBOARD
from src.bot.structures.keyboards.menu import MENU_KEYBOARD
from src.bot.structures.keyboards.dreams import CANCEL_BUTTON


@register_router.message(F.text.lower() == 'ok, давай начнем')
async def register_confirmation(message: Message, state: FSMContext, db):
    user = await db.user.user_register_check(active_user_id=message.from_user.id)

    if user is None:
        await state.set_state(RegisterGroup.age)
        welcome_text = (
            "🎉 **Отлично! Начинаем регистрацию!** 🎉\n\n"
            "Давай познакомимся поближе! Это займет всего несколько минут.\n\n"
            "**Шаг 1 из 5: Возраст** 📅\n"
            "Сколько тебе лет? Просто введи число."
        )
        await message.answer(welcome_text, reply_markup=CANCEL_BUTTON, parse_mode="MARKDOWN")
    else:
        await message.answer(
            f"Привет, *{user.name if user.name else message.from_user.first_name}*! Ты уже зарегистрирован.\n\n"
            f"1. Просмотреть список желаний\n2. Просмотреть мои желания\n3. Изменить имя",
            reply_markup=MENU_KEYBOARD,
            parse_mode="MARKDOWN"
        )


@register_router.message(F.text.lower() == "отмена")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()

    if current_state is not None:
        await state.clear()
        await message.answer(f"Вы отменили {emoji.emojize(':smiling_face_with_tear:')}",
                             reply_markup=REGISTER_START_CONFIRM)


@register_router.message(RegisterGroup.age)
async def register_gender_handler(message: Message, state: FSMContext):
    age_text = message.text.strip()

    if not age_text.isdigit():
        return await message.answer("Пожалуйста, введите корректный возраст. Это должно быть число.")

    age = int(age_text)

    if age <= 0:
        return await message.answer("Пожалуйста, введите корректный возраст. Это должно быть положительное число.")

    await state.update_data(age=age)
    await state.set_state(RegisterGroup.gender)

    gender_text = (
        "✅ **Возраст сохранен!** ✅\n\n"
        "**Шаг 2 из 5: Пол** 👤\n"
        "Выбери свой пол из предложенных вариантов ниже."
    )
    return await message.answer(gender_text, reply_markup=REGISTER_USER_GENDER, parse_mode="MARKDOWN")


@register_router.message(RegisterGroup.gender)
async def register_country_handler(message: Message, state: FSMContext):
    gender = message.text.strip().lower()

    if gender not in ["мужчина", "женщина"]:
        return await message.answer("Пожалуйста, выберите ваш пол из предложенных вариантов.")

    await state.update_data(gender=gender)
    await state.set_state(RegisterGroup.country)

    country_text = (
        "✅ **Пол выбран!** ✅\n\n"
        "**Шаг 3 из 5: Город** 🌍\n"
        "Из какого ты города? Это поможет найти единомышленников поблизости!"
    )
    return await message.answer(country_text, reply_markup=REGISTER_USER_COUNTRY, parse_mode="MARKDOWN")


@register_router.message(RegisterGroup.country)
async def register_name_handler(message: Message, state: FSMContext):
    country = message.text.strip()

    if not country:
        return await message.answer("Пожалуйста, укажите вашу страну.")

    await state.update_data(country=country)
    await state.set_state(RegisterGroup.name)

    name_text = (
        "✅ **Город указан!** ✅\n\n"
        "**Шаг 4 из 5: Имя** ✨\n"
        "Как мне тебя называть? Можешь использовать свое настоящее имя или придумать красивое прозвище!"
    )
    return await message.answer(name_text, reply_markup=CANCEL_BUTTON, parse_mode="MARKDOWN")


@register_router.message(RegisterGroup.name)
async def register_user_handler(message: Message, state: FSMContext, db):
    try:
        data = await state.get_data()
        user_id = message.from_user.id
        user_name = message.from_user.username if message.from_user.username else None
        name = data.get('name') or message.text
        age = int(data.get('age'))
        gender = data.get('gender')
        country = data.get('country')

        # Проверяем, не зарегистрирован ли уже пользователь
        existing_user = await db.user.user_register_check(active_user_id=user_id)
        if existing_user:
            await state.clear()
            await message.answer(
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

        # Создаем нового пользователя
        await db.user.new(user_id=user_id, user_name=user_name, name=name, age=age,
                          gender=gender, country=country)
        await state.clear()

        success_text = (
            f"🎉 **Поздравляем с успешной регистрацией!** 🎉\n\n"
            f"Привет, **{name}**! 👋\n\n"
            "**✅ Регистрация завершена успешно!**\n"
            "Теперь ты полноправный участник сообщества Wanty!\n\n"
                    "**🏆 Достижения:**\n"
        "• +25 очков за регистрацию\n"
        "• Разблокировано достижение 'Новый участник'\n\n"
        "**🚀 Что дальше?**\n"
        "• Просматривай желания других пользователей\n"
        "• Создавай свои желания (+15 очков за каждое)\n"
        "• Изучай категории желаний\n"
        "• Находи единомышленников\n"
        "• Общайся и знакомься!\n\n"
            "**💡 Совет:** Начни с просмотра желаний - нажми кнопку 'Желания' ниже!"
        )
        
        return await message.answer(
            success_text,
            reply_markup=MENU_KEYBOARD,
            parse_mode="MARKDOWN"
        )
        
        # Отправляем inline кнопки для дополнительных функций
        from src.bot.structures.keyboards.menu import ADDITIONAL_FEATURES_MARKUP
        
        await message.answer(
            "🔧 **Дополнительные возможности:**",
            reply_markup=ADDITIONAL_FEATURES_MARKUP,
            parse_mode="MARKDOWN"
        )
    except Exception as e:
        print(f"Error in register_user_handler: {e}")
        await message.answer(
            'Произошла ошибка при регистрации. Пожалуйста, попробуйте еще раз или свяжитесь с поддержкой.',
            reply_markup=REGISTER_START_CONFIRM
        )
