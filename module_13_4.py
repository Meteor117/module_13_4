from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

import asyncio


api = ''# API key
bot = Bot(token=api)#переменная бота, которая  хранит объект бота. Токен=API
dp = Dispatcher(bot, storage=MemoryStorage())#переменная диспетчера, которая будет Dispatcher'ом с ботом в качестве
                                            # аргумента. В качестве storage используется MemoryStorage.


class UserState(StatesGroup):
    age = State()#возраст
    growth = State()#рост
    weight = State()#вес

@dp.message_handler(commands = ['start'])
async def start(message):
    await message.answer('Привет! Я бот, помогающий твоему здоровью. Хочешь узнать свою норму калорий для похудения '
                         'или сохранения веса - введи Calories')


@dp.message_handler(text='Calories')
async def set_age(message):
    await message.answer('Введите свой возраст (полных лет):')#внутри функции мы оправляем сообщение с просьбой сообщить возраст
    await UserState.age.set()#установка состояния и запись возраста клиента

@dp.message_handler(state=UserState.age)#хендлер состояния, ожидает поступления сообщения с возрастом
async def set_growth(message, state):
    await state.update_data(age=message.text)#записываем в словарь 'age'
    await message.answer('Введите свой рост (см):')#возврат заказчику сообщения с просьбой сообщить рост
    await UserState.growth.set()#установка состояния и запись роста клиента

@dp.message_handler(state=UserState.growth)#хендлер состояния, ожидает поступления сообщения с ростом
async def set_weight(message, state):#хендлер для работы с состояниями (FSM)
    await state.update_data(growth=message.text)#записываем в словарь 'growth'
    await message.answer("Введите свой вес (кг):")#возврат заказчику сообщения с просьбой сообщить свой вес
    await UserState.weight.set()#установка состояния и запись веса клиента

@dp.message_handler(state=UserState.weight)#хендлер состояния, ожидает поступления сообщения с весом
async def send_calories(message, state):
    await state.update_data(weight=message.text)# записываем в словарь 'weight'
    data = await state.get_data()#для получение  данных состояния после их обновления

    #Упрощенный вариант формулы Миффлина-Сан Жеора:
    #для мужчин: 10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) + 5;
    #ля женщин: 10 x вес (кг) + 6,25 x рост (см) – 5 x возраст (г) – 161.

    man_calories = 10 * float(data['weight']) + 6.25 * float(data['growth']) - 5 * float(data['age']) + 5
    woman_calories = 10 * float(data['weight']) + 6.25 * float(data['growth']) - 5 * float(data['age']) - 161
    await message.answer(f'Ваша норма калорий: {man_calories} калорий, если вы мужчина\n '#возврат заказчику результатов
                         f'                  '
                         f'                    {woman_calories} калорий, если вы женщина')



    await state.finish()#закрываем машину после завершения ее работы с сохранением полученных данных


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)#переменная executor, которая будет запускать диспетчер
