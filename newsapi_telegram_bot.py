from bot_data import BOT_TOKEN, NEWSAPI_TOKEN

from datetime import datetime

from enum import Enum

import numpy as np

import requests

from telepot import Bot, DelegatorBot, glance
from telepot.delegate import per_application, create_open, pave_event_space, per_chat_id
from telepot.helper import ChatHandler, Monitor
from telepot.loop import MessageLoop

from threading import Thread

import time

from typing import List

CHAR_TO_ESCAPE_LIST = ['(', ')', '.', '=', '-']


class BotCommand(Enum):
	SUBSCRIBE = '/sub'
	UNSUBSCRIBE = '/unsub'


def broadcast_task(broadcast: callable):
	while True:
		if datetime.now().hour == 9:
			broadcast()

		time.sleep(3600)


class NewsApiTelegramBot(ChatHandler):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		# make sure ChatHandler accepts all incoming msg
		self.listener.capture([lambda msg: True])

		self.subscriber_list: List[int] = list()
		self.scheduledBroadcaster: Thread = Thread(target=broadcast_task, args=(self.broadcast_news,))
		self.scheduledBroadcaster.start()

	def sanitiseString(self, string: str) -> str:
		if not string:
			return ''

		for char in CHAR_TO_ESCAPE_LIST:
			string = string.replace(char, '\\' + char)

		return string

	def on_chat_message(self, msg):
		content_type, _, chat_id = glance(msg)

		try:
			command = msg['text'].strip().lower()
		except KeyError:
			# ignore non-text messages
			return

		if command == BotCommand.SUBSCRIBE.value:
			if not chat_id in self.subscriber_list:
				self.subscriber_list.append(chat_id)
				self.bot.sendMessage(chat_id, 'You are now in my subscriber list.')
		elif command == BotCommand.UNSUBSCRIBE.value:
			try:
				self.subscriber_list.remove(chat_id)
				self.bot.sendMessage(chat_id, 'You are no longer in my subscriber list.')
			except ValueError:
				self.bot.sendMessage(chat_id, 'You have not subscribed to me yet.')
		elif command == '/test':
			print('<< test >>')
			self.broadcast_news()

	def getArticleList(self) -> List[dict]:
		url = r'https://newsapi.org/v2/top-headlines?country={}&apiKey={}'.format('sg', NEWSAPI_TOKEN)

		resp = requests.get(url)

		if resp.status_code == 200:
			return resp.json()['articles']
		else:
			return []

	def generateNewsMessage(self, article: dict) -> str:
		source = self.sanitiseString(article['source']['name'])
		author = self.sanitiseString(article['author'])
		title = self.sanitiseString(article['title'])
		description = self.sanitiseString(article['description'])
		url = article['url']

		message = '\[_*{}*_\] *{}*\n_by {}_\n\n{}\n\nRead more [here]({})\.'.format(source.split('\.')[0].upper(), title, author, description, url)

		return message

	def broadcast_news(self):
		article_list = self.getArticleList()

		# consider using thread pool
		for subscriber in self.subscriber_list:
			for article in article_list:
				message = self.generateNewsMessage(article)
				self.bot.sendMessage(subscriber, message, parse_mode='MarkdownV2')


def main():
	bot = DelegatorBot(BOT_TOKEN, [ pave_event_space()(per_application(), create_open, NewsApiTelegramBot, timeout=np.inf) ])
	MessageLoop(bot).run_as_thread()

	while 1:
		time.sleep(10)

if __name__ == '__main__':
	main()

