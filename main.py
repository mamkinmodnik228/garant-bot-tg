import logging
import asyncio
from aiogram import Bot, Dispatcher, executor, types
from sqlite import SQLite
from buttons import keyboard
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import re
from pyqiwip2p import QiwiP2P
from pyqiwip2p.types import QiwiCustomer
import random

logging.basicConfig(level=logging.INFO)

token = '1708389560:AAEUyLYSnLIBJ4ljznBSol7OGvxLQFdZ3sw'
bot = Bot(token=token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

db = SQLite('database.db')

qiwi_token = '56cb024ab4b044c96af183fea5c280f7'
p2p = QiwiP2P(auth_key=qiwi_token)

class Form(StatesGroup):
    creator_id = ''
    seller_id = ''
    customer_id = ''
    money = 0
    receiver_id = State()
    continue_deal = State()
    teams = State()
    cash = State()
    deals = State()

class Deposit(StatesGroup):
    cash = State()


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if db.checkMember(message.from_user.id) is None:

        db.addMember(message.from_user.id, message.from_user.username)
        await message.answer('Вы зарегистрированы!', reply_markup=await keyboard('start'))

    else:
        await message.answer('Личный кабинет', reply_markup=await keyboard('start'))


@dp.message_handler(commands=['stats'])
async def stats(message: types.Message):
    if db.checkMember(message.from_user.id) is None:
        await message.answer('Вы не зарегистрированы.')
    else:
        stats = db.stats(message.from_user.id)
        text = f"🔍 Профиль @{message.from_user.username}\nID: {stats[0]}\nБаланс: {stats[1]}\n➖➖➖➖➖➖➖➖➖➖➖\n💰Продажи: {stats[2]} шт\n🛒Покупки: {stats[3]} шт\n➖➖➖➖➖➖➖➖➖➖➖"
        await message.answer(text, reply_markup=await keyboard('user_profile'))


@dp.message_handler(commands=['deals'])
async def deals(message: types.Message):
    if db.checkMember(message.from_user.id) is None:
        await message.answer('Вы не зарегистрированы.')
    else:
        await message.answer('Выберите тип сделки', reply_markup=await keyboard('deals'))


@dp.message_handler(commands=['search'])
async def search(message: types.Message):
    if db.checkMember(message.from_user.id) is None:
        await message.answer('Вы не зарегистрированы.')
    else:
        await Form.receiver_id.set()
        await message.answer('Введите ник пользователя с которым хотите провести сделку')


@dp.message_handler(state=Form.receiver_id)
async def process_receiver_id(message: types.Message, state: FSMContext):
    async with state.proxy() as data:

        if message.text.startswith('@'):
            data['receiver_id'] = message.text[1:]
        else:
            data['receiver_id'] = message.text

        if db.checkUser(data['receiver_id']) is None:
            await message.answer('Данный пользователь не найден')
            await state.finish()
        else:
            if message.from_user.username == data['receiver_id']:
                await message.answer('Вы ввели свой ник')
            else:
                stats = db.stats_by_username(data['receiver_id'])
                if stats is None:
                    await message.answer('Пользователь не зарегистрирован')
                    await state.finish()
                else:
                    text = f"🔍 Пользователь @{data['receiver_id']}\nID: {stats[0]}\n➖➖➖➖➖➖➖➖➖➖➖\n💰Продажи: {stats[1]} шт\n🛒Покупки: {stats[2]} шт\n➖➖➖➖➖➖➖➖➖➖➖\n"
                    await message.answer(text, reply_markup=await keyboard('profile'))
                    await Form.next()
                    # state.proxy()['second_id'] = stats[0]
                    data['creator_id'] = message.from_user.id
                    data['receiver_id'] = stats[0]


@dp.message_handler(state=Form.continue_deal)
async def process_continue(message: types.Message, state: FSMContext):

    if message.text == 'Начать сделку':
        async with state.proxy() as data:
            if db.getDealCustomer(message.from_user.id) is None and db.getDealSeller(message.from_user.id) is None:
                if db.getDealCustomer(data['receiver_id']) is None and db.getDealSeller(data['receiver_id']) is None:
                    await message.answer('Кем вы будете в этой сделке', reply_markup=await keyboard('deal_ts'))
                    await Form.next()
                else:
                    await message.answer('Данный пользователь уже в сделке!')
            else:
                await message.answer('Вы в сделке!')

    elif message.text == 'Отзывы':
        pass
    elif message.text == 'Выход':
        await state.finish()
        await message.answer('Личный кабинет', reply_markup=await keyboard('start'))


@dp.message_handler(state=Form.teams)
async def process_teams(message: types.Message, state: FSMContext):
    async with state.proxy() as data:

        if message.text == 'Продавец':
            data['seller_id'] = message.from_user.id
            data['customer_id'] = data['receiver_id']
            await message.answer('Вы выбрали Продавец!', reply_markup=await keyboard('start'))
            await Form.next()
            await message.answer('Введите сумму сделки')

        elif message.text == 'Покупатель':
            data['seller_id'] = data['receiver_id']
            data['customer_id'] = message.from_user.id
            await message.answer('Вы выбрали Покупатель!', reply_markup=await keyboard('start'))
            await Form.next()
            await message.answer('Введите сумму сделки')

        else:
            await state.finish()
            await message.answer('Вы можете выбрать только Покупатель или Продавец',
                                 reply_markup=await keyboard('start'))


@dp.message_handler(state=Form.cash)
async def process_cash(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if re.search('\D', message.text):
            await message.answer('Вы ввели лишние символы')
            await state.finish()
        else:
            data['cash'] = message.text
            if int(message.text) > db.getCash(message.from_user.id)[0]:
                await message.answer(
                    f'Вы ввели сумму сделки больше чем ваш баланс ({data["cash"]} > {db.getCash(message.from_user.id)[0]})',
                    reply_markup=await keyboard('start'))
                await state.finish()

            if int(message.text) > db.getCash(data['receiver_id'])[0]:
                await message.answer('У пользователя нет такой суммы!')
                await state.finish()
            if data['customer_id'] == message.from_user.id:
                if int(message.text) > db.getCash(message.from_user.id)[0]:
                    await message.answer(
                        f'Сумма, которую вы ввели превышает ваш баланс ({data["cash"]} > {db.getCash(message.from_user.id)[0]})',
                        reply_markup=await keyboard('start'))
                    await state.finish()
            else:
                await message.answer(f"Сумма сделки ({data['cash']}) выбрана")
                await Form.next()
                text = f"Продавец: {db.getNameByID(data['seller_id'])[0]}\nПокупатель: {db.getNameByID(data['customer_id'])[0]}\nСумма сделки: {data['cash']}"
                db.addDeal(data['seller_id'], data['customer_id'], data['cash'])
                await message.answer('Сделка создана!\n' + text)
                await bot.send_message(data['receiver_id'],
                                        f"Сделка от {db.getNameByID(data['creator_id'])[0]}\n{text}",
                                        reply_markup=await keyboard('new_deal'))
                await state.finish()


@dp.callback_query_handler(lambda call: True)
async def answer(call):
    if call.data == 'start_deal':
        await bot.send_message(call.from_user.id, 'Кем вы будете в этой сделке', reply_markup=await keyboard('deal_ts'))

    elif call.data == 'new_deal_accept':

        if db.getDealSeller(call.from_user.id) is None:
            dealInfo = db.getDealCustomer(call.from_user.id) # seller_id,customer_id,money,active,cancelled,end

            await bot.send_message(dealInfo[1],
                                   f'Вы приняли сделку с {db.getNameByID(dealInfo[0])[0]}\nПодтвердите сделку, только когда продавец выдал товар',
                                   reply_markup=await keyboard('deal_confirm'))
            await bot.send_message(dealInfo[0],
                                   f'Покупатель {db.getNameByID(dealInfo[1])[0]} принял сделку с вами! Дождитесь подтверждения заказа')

            db.withdrawBalance(dealInfo[1], dealInfo[3])
            db.setDealActive(dealInfo[0], 1)

        elif db.getDealCustomer(call.from_user.id) is None:

            dealInfo = db.getDealsSeller(call.from_user.id) # seller_id,customer_id,money,active,cancelled,end

            await bot.send_message(dealInfo[1],
                                   f'Вы приняли сделку с {db.getNameByID(dealInfo[0])[0]}\nПодтвердите сделку, только когда продавец выдал товар',
                                   reply_markup=await keyboard('deal_confirm'))
            await bot.send_message(dealInfo[0],
                                   f'Покупатель {db.getNameByID(dealInfo[1])[0]} принял сделку с вами! Дождитесь подтверждения заказа')

            db.withdrawBalance(dealInfo[1], dealInfo[3])
            db.setDealActive(dealInfo[0], 1)

        else:
            print('New Deal Accept without somebody')

    elif call.data == 'new_deal_decline':

        deals = db.getDealSeller(call.from_user.id)
        if deals is None:
            deals = db.getDealCustomer(call.from_user.id)
            await bot.send_message(deals[0], f'Покупатель {db.getNameByID(deals[1])[0]} отказался от сделки')
            await bot.send_message(deals[1], f'Вы отказались от сделки с {db.getNameByID(deals[0])[0]}')
            db.deleteDeal(deals[0])
        else:
            await bot.send_message(deals[0], f'Покупатель {db.getNameByID(deals[1])[0]} отказался от сделки')
            await bot.send_message(deals[1], f'Вы отказались от сделки с {db.getNameByID(deals[0])[0]}')
            db.deleteDeal(deals[0])


    elif call.data == 'dc_accept':

        deals = db.getDealCustomer(call.from_user.id)
        if deals:
            money = deals[2] - (deals[2] * 0.05)
            db.giveBalance(deals[0], money)
            seller_balance = db.getBalance(deals[0])[0]

            await bot.send_message(deals[0], f'Покупатель {db.getNameByID(deals[1])[0]} подтвердил заказ! На ваш баланс зачислено {money}\nВаш баланс составляет: {seller_balance}')
            await bot.send_message(deals[1], f'Заказ успешно подтвержден')
            db.setDealsCustomer(deals[1])
            db.setDealsSeller(deals[0])
            db.setDealActive(deals[0], 0)
            db.setDealEnd(deals[0], 1)

    elif call.data == 'dc_decline':

        if db.getDealSeller(call.from_user.id) is None:
            dealInfo = db.getDealCustomer(call.from_user.id) # seller_id,customer_id,money,active,cancelled,end

            await bot.send_message(dealInfo[1], f'Вы отклонили заказ с {db.getNameByID(dealInfo[0])[0]}',
                                   reply_markup=await keyboard('start'))
            await bot.send_message(dealInfo[0],
                                   f'Покупатель {db.getNameByID(dealInfo[1])[0]} отклонил заказ с вами!')

            db.giveBalance(dealInfo[0], dealInfo[3])
            db.setDealActive(dealInfo[0], 0)
            db.setDealEnd(dealInfo[0], 1)

        elif db.getDealCustomer(call.from_user.id) is None:

            dealInfo = db.getDealsSeller(call.from_user.id) # seller_id,customer_id,money,active,cancelled,end

            await bot.send_message(dealInfo[1], f'Вы отклонили заказ с {db.getNameByID(dealInfo[0])[0]}',
                                   reply_markup=await keyboard('start'))

            await bot.send_message(dealInfo[0],
                                   f'Покупатель {db.getNameByID(dealInfo[1])[0]} отклонил заказ с вами!')

            db.giveBalance(dealInfo[0], dealInfo[3])
            db.setDealActive(dealInfo[0], 0)
            db.setDealEnd(dealInfo[0], 1)

    elif call.data == 'deposit':

        await Deposit.cash.set()
        await bot.send_message(call.from_user.id, 'Введите сумму')


    elif call.data == 'withdraw':
        pass

    elif call.data == 'user_active_deals':
        await bot.send_message(call.from_user.id, 'Вывести ваши активные сделки где вы ',
                               reply_markup=await keyboard('deals_active'))

    elif call.data == 'user_past_deals':
        await bot.send_message(call.from_user.id, 'Вывести ваши последние сделки где вы ',
                               reply_markup=await keyboard('deals_none'))

    elif call.data == 'user_active_deals_seller':
        deals = db.getDealsActiveSeller(call.from_user.id)
        if len(deals) == 0:
            await bot.send_message(call.from_user.id, 'Нет активных сделок, где вы продавец')
        else:
            text = []
            for x in deals:
                text.append(f'Покупатель: {db.getNameByID(x[0])[0]}\nСумма сделки: {x[1]}\n\n')

            await bot.send_message(call.from_user.id, ''.join(text))

    elif call.data == 'user_active_deals_customer':
        deals = db.getDealsActiveCustomer(call.from_user.id)
        if len(deals) == 0:
            await bot.send_message(call.from_user.id, 'Нет активных сделок, где вы покупатель')
        else:
            text = []
            for x in deals:
                text.append(f'Продавец: {db.getNameByID(x[0])[0]}\nСумма сделки: {x[1]}\n\n')

            await bot.send_message(call.from_user.id, ''.join(text))

    elif call.data == 'user_deals_seller':
        deals = db.getDealsSeller(call.from_user.id)
        if len(deals) == 0:
            await bot.send_message(call.from_user.id, 'Нет сделок, где вы продавец')
        else:
            text = []
            for x in deals:
                text.append(f'Покупатель: {db.getNameByID(x[0])[0]}\nСумма сделки: {x[1]}\n\n')

            await bot.send_message(call.from_user.id, ''.join(text))


    elif call.data == 'user_deals_customer':
        deals = db.getDealsCustomer(call.from_user.id)
        if len(deals) == 0:
            await bot.send_message(call.from_user.id, 'Нет сделок, где вы покупатель')
        else:
            text = []
            for x in deals:
                text.append(f'Продавец: {db.getNameByID(x[0])[0]}\nСумма сделки: {x[1]}\n\n')

            await bot.send_message(call.from_user.id, ''.join(text))

@dp.message_handler(state=Deposit.cash)
async def deposit_get_cash(message: types.Message, state = FSMContext):

    if message.text.isdigit():
        async with state.proxy() as data:

            data['cash'] = message.text
            amount = message.text
            lifetime = 10  # Форма будет жить 15 минут
            comment = f'{message.from_user.id} payment'  # Комментарий
            bill_id = random.randint(0, 9999999)
            db.deposit(bill_id, message.from_user.id, amount, comment, 'wait')
            bill = p2p.bill(bill_id=bill_id, amount=amount, comment=comment)  # Выставление счета
            message_payment = await bot.send_message(message.from_user.id,
                                                     text=f'У вас есть {lifetime} минут на оплату!\nСумма: {amount}₽\nСсылка:\n{bill.pay_url}')  # Отправляем ссылку человеку

@dp.message_handler(commands=['cash'])
async def get_cash(message: types.Message):

    cash = db.getBalance(message.from_user.id)[0]
    await message.answer(f'cash: {cash}')

@dp.message_handler(content_types=['text'])
async def text(message: types.Message):
    if message.text == 'О нас':
        await message.answer(
            'По всем вопросам: @kings_555\nНаш чат: https://t.me/Yslugi_LOUIS_VUITTON\nИнструкция по использованию: https://t.me/Yslugi_LOUIS_VUITTON')

    elif message.text == 'Мой профиль':
        await stats(message)

    elif message.text == 'Сделки':
        await deals(message)

    elif message.text == 'Поиск пользователя':
        await search(message)

async def check_payments():
    payments = db.getAllPayments()

    if payments is None:
        print('No new additions found')

    for x in range(0, len(payments)):
        try:
            status = p2p.check(bill_id=payments[x][0]) # bill_id - номер платежа
            if status.status == 'PAID': # Если статус счета оплачен (PAID)

                userid = db.getUserIdFromPayment(payments[x][0])[0]
                amount = db.getAmountFromPayment(payments[x][0])[0]

                db.updatePaymentStatus(payments[x][0], 'success')
                await bot.send_message(text=f'Оплата на {amount} руб. прошла успешно!', chat_id = userid)
                db.giveBalance(userid, int(amount))
        except Exception as error:
            print(error)

def repeat_payment(coro, loop):
    asyncio.ensure_future(coro(), loop=loop)
    loop.call_later(8, repeat_payment, coro, loop)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.call_later(8, repeat_payment, check_payments, loop)
    executor.start_polling(dp, skip_updates=True)
