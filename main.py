#!/usr/bin/python3

import telepot
import time

from os.path import join, dirname
from telepot.loop import MessageLoop

token = open(join(dirname(__file__), 'TOKEN')).read().strip()
bot = telepot.Bot(token)

def handle_message(msg):
	content_type, chat_type, chat_id = telepot.glance(msg)
	print(content_type, chat_type, chat_id)
	print(msg)

	if content_type == 'text':
		bot.sendMessage(chat_id, msg['text'])

MessageLoop(bot, handle_message).run_as_thread()

while True:
	time.sleep(10)

