from datetime import datetime

from enum import Enum

from telepot import Bot, DelegatorBot, glance
from telepot.delegate import per_application, create_open, pave_event_space
from telepot.helper import ChatHandler
from telepot.loop import MessageLoop

from typing import List


class BotCommand(Enum):
	SUBSCRIBE = '/sub'
	UNSUBSCRIBE = '/unsub'


class NewsApiTelegramBot(ChatHandler):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.subscriber_list: List[int] = list()

	def on_chat_message(self, msg):
		content_type, _, chat_id = glance(msg)

		try:
			command = msg['text'].strip().lower()
		except KeyError:
			# ignore non-text messages
			return

		if command == BotCommand.SUBSCRIBE:
			if not chat_id in self.subscriber_list:
				subscriber_list.append(chat_id)
				self.sender.sendMessage('You are now in my subscriber list.')
		elif command == BotCommand.UNSUBSCRIBE:
			try:
				self.subscriber_list.remove(chat_id)
				self.sender.sendMessage('You are no longer in my subscriber list.')
			except ValueError:
				self.sender.sendMessage('You have not subscribed to me yet.')

	def getNewsList(self):
		pass

	def broadcast_news(self):
		news_list = self.getNewsList()

		# consider using thread pool
		for subscriber in self.subscriber_list:
			for news in news_list:
				self.bot.sendMessage(subscriber, news)
