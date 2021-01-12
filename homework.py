import os
import time

import requests
import telegram
import logging
from dotenv import load_dotenv

load_dotenv()

PRACTICUM_API = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

logging.basicConfig(
    level=logging.DEBUG,
    filename='program.log',
    filemode='w',
    format='%(asctime)s; %(levelname)s; %(name)s;'
           '%(message)s; %(lineno)s'
)


def get_homework_statuses(current_timestamp):
    params={'from_date': current_timestamp}
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    try:
        homework_statuses = requests.get(
            PRACTICUM_API,
            params=params,
            headers=headers
        )
        return homework_statuses.json()
    except requests.RequestException as error:
        return logging.error(error, exc_info=True)


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    if homework.get('status') == 'rejected':
        verdict = 'К сожалению в работе нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def send_message(message, bot_client):
    return bot_client.send_message(
        chat_id=CHAT_ID,
        text=message
    )


def main():
    logging.debug('Bot lounched')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(
                    parse_homework_status(new_homework.get('homeworks')[0]),
                    bot)
                logging.info('Message sent to Telegram')
            current_timestamp = new_homework.get(
                'current_date',
                current_timestamp)
            time.sleep(300)
        except Exception as error:
            logging.error(error, exc_info=True)
            send_message(f'Бот столкнулся с ошибкой: {error}', bot)
            time.sleep(5)


if __name__ == '__main__':
    main()
