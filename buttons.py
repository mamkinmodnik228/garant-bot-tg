import asyncio
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

async def keyboard(data, message = None):

    if data == 'start':
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = KeyboardButton('Поиск пользователя')
        button2 = KeyboardButton('Мой профиль')
        button3 = KeyboardButton('Сделки')
        button4 = KeyboardButton('О нас')
        keyboard.add(button1, button2).add(button3, button4)

    elif data == 'deals':
        keyboard = InlineKeyboardMarkup(resize_keyboard=True)
        button1 = InlineKeyboardButton('Активные', callback_data='user_active_deals')
        button2 = InlineKeyboardButton('Прошедшие', callback_data='user_past_deals')
        keyboard.add(button1, button2)

    elif data == 'deals_active':
        keyboard = InlineKeyboardMarkup(resize_keyboard=True)
        button1 = InlineKeyboardButton('Продавец',callback_data='user_active_deals_seller')
        button2 = InlineKeyboardButton('Покупатель', callback_data='user_active_deals_customer')
        keyboard.add(button1, button2)

    elif data == 'deals_none':
        keyboard = InlineKeyboardMarkup(resize_keyboard=True)
        button1 = InlineKeyboardButton('Продавец',callback_data='user_deals_seller')
        button2 = InlineKeyboardButton('Покупатель', callback_data='user_deals_customer')
        keyboard.add(button1, button2)

    elif data == 'deal_ts':
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = KeyboardButton('Продавец',callback_data='new_deal_seller')
        button2 = KeyboardButton('Покупатель', callback_data='new_deal_customer')
        keyboard.add(button1, button2)

    elif data == 'new_deal':
        keyboard = InlineKeyboardMarkup(resize_keyboard=True)
        button1 = InlineKeyboardButton('Принять', callback_data='new_deal_accept')
        button2 = InlineKeyboardButton('Отклонить', callback_data='new_deal_decline')
        keyboard.add(button1, button2)

    elif data == 'profile':
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = KeyboardButton('Начать сделку')
        button2 = KeyboardButton('Отзывы')
        button3 = KeyboardButton('Выход')
        keyboard.add(button1, button2)

    elif data == 'deal_confirm':
        keyboard = InlineKeyboardMarkup(resize_keyboard=True)
        button1 = InlineKeyboardButton('Подтвердить заказ', callback_data='dc_accept')
        button2 = InlineKeyboardButton('Отменить заказ', callback_data='dc_decline')
        keyboard.add(button1, button2)

    elif data == 'user_profile':
        keyboard = InlineKeyboardMarkup(resize_keyboard=True)
        button1 = InlineKeyboardButton('Пополнить баланс', callback_data='deposit')
        button2 = InlineKeyboardButton('Вывести деньги', callback_data='withdraw')
        button3 = InlineKeyboardButton('Мои отзывы', callback_data='reviews')
        keyboard.add(button1, button2).add(button3)

    return keyboard