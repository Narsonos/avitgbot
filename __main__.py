import logging
import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import Router
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import bot_token, db_file, user_id
from db import init_db, AvitoRequest
from parser import Parser

import sys
import requests
import datetime
from dataclasses import dataclass

dp = Dispatcher()
router = Router()
dp.include_router(router)
bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))



class Form(StatesGroup):
    adding_request = State()
    deleting_request = State()


class MessageBuilder:
    @staticmethod
    def describe_latest_for_request(request,offer):
        return f"[OFFER]: <a href='{offer.link}'>{offer.title}</a>\n[PRICE]: {offer.price}\n[REQUEST]: <a href='{request.link}'>{request.name}</a>\n[DESCRIPTION]:\n{offer.desc}"

    @staticmethod
    def list_requests(requests):
        response = "Your requests:\n"
        for request in requests:
            response += f"{request.id}. <a href='{request.link}'>{request.name}</a> \n"
        return response




async def track_requests():
    while True:
        with sqlite3.connect(db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM requests')
            rows = cursor.fetchall()
            for row in rows:
                await check_for_new_offers(cursor, row)
                await asyncio.sleep(15)  # Sleep for a minute between checks
            await asyncio.sleep(180)


async def check_for_new_offers(cursor, request):
    request = AvitoRequest(*request)
    request.latest_offer_date = datetime.datetime.strptime(request.latest_offer_date,'%Y-%m-%d %H:%M:%S.%f')

    offer = await fetch_latest_offer(request.link)
    if offer and (request.latest_offer_id != offer.id) and (request.latest_offer_date < offer.date):  # Compare with stored latest offer

        msg = MessageBuilder.describe_latest_for_request(request,offer)
        await bot.send_message(user_id, msg, parse_mode=ParseMode.HTML)

        cursor.execute('UPDATE requests SET latest_offer_link = ?, latest_offer_id = ?, latest_offer_date = ? WHERE id = ?', (offer.link,offer.id,offer.date,request.id))
        cursor.connection.commit()

async def fetch_latest_offer(link):
    return parser.get_first(link)  # Example ID


@router.message(Command('start','help'))
async def send_welcome(message: types.Message):
    await message.reply("Welcome! Use /add to add a request, /delete to remove one, and /status to check requests.")

@router.message(Command('latest'))
async def check_latest(message: types.Message):
    with sqlite3.connect(db_file) as conn:
        sent_message = await bot.send_message(user_id, "Processing the request...", parse_mode=ParseMode.HTML)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM requests')
        rows = cursor.fetchall()
        requests = [AvitoRequest(*row) for row in rows]

        response = ""
        try:
            for i,request in enumerate(requests):
                await bot.edit_message_text(text=f"Processing the request {i}...",chat_id=user_id,message_id=sent_message.message_id)
                print(request)
                offer = await fetch_latest_offer(request.link)
                response += MessageBuilder.describe_latest_for_request(request,offer) + '\n\n'
                await asyncio.sleep(5)
            await bot.edit_message_text(text=response,chat_id=user_id,message_id=sent_message.message_id)
        except Exception as e:
            await bot.edit_message_text(text=f'Exception: {e}',chat_id=user_id,message_id=sent_message.message_id)


@router.message(Command('add'))
async def add_request(message: types.Message, state: FSMContext):
    await state.set_state(Form.adding_request)
    await message.reply("Send me the name of the request and link on the next line.")

@router.message(Form.adding_request)
async def process_add_request(message: types.Message, state: FSMContext):
    try:
        name, link = message.text.split('\n')
        minimal_date = datetime.datetime.min + datetime.timedelta(microseconds=1)
        with sqlite3.connect(db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO requests(link, latest_offer_link,latest_offer_id,latest_offer_date, name) VALUES(?, ?, ?, ?, ?)', 
                           (link.strip(), None, None,minimal_date, name))  # Store None as the initial latest_offer_link
            conn.commit()
        await message.reply("Request added successfully!")
    except Exception as e:
        await message.reply(f"Error adding request. Please ensure you provide a valid link and name. {e}")
    finally:
        await state.clear()

@router.message(Command('delete'))
async def delete_request(message: types.Message, state: FSMContext):
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM requests')
        requests = cursor.fetchall()
        requests = [AvitoRequest(*req) for req in cursor.fetchall()]

    if not requests:
        await message.reply("No requests found!")
        return
    
    response = MessageBuilder.list_requests(requests)
    
    await state.set_state(Form.deleting_request)
    await message.reply(response + "Select the number of the request to delete.", parse_mode=ParseMode.HTML)


@router.message(Form.deleting_request)
async def process_delete_request(message: types.Message, state: FSMContext):
    try:
        index = int(message.text)
        with sqlite3.connect(db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM requests')
            requests = [AvitoRequest(*req).id for req in cursor.fetchall()]
            if index in requests:
                cursor.execute('DELETE FROM requests WHERE id = ?', (str(index)))
                conn.commit()
                await message.reply("Request deleted successfully!")
            else:
                await message.reply("Invalid request number.")
    except Exception as e:
        await message.reply(f"Error deleting request.{e}")
    finally:
        await state.clear()

@router.message(Command("status"))
async def status_requests(message: types.Message):
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM requests')
        requests = [AvitoRequest(*req) for req in cursor.fetchall()]


    if not requests:
        await message.reply("No requests being tracked!")
        return

    response = MessageBuilder.list_requests(requests)
    await message.reply(response)


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    init_db() 
    loop = asyncio.get_event_loop()
    loop.create_task(track_requests())

    # And the run events dispatching
    await dp.start_polling(bot)

if __name__ == "__main__":
    parser = Parser()
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())