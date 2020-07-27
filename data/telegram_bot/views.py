#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This is a simple echo bot using decorators and webhook with flask
# It echoes any incoming text messages and does not use the polling method.

import logging
import time
import telebot
from telebot import types
from telebot import apihelper

import flask
from flask import request

from app import app
import mongodb_query
import messages
from config import Config

import json
import requests
import ast





bot = telebot.TeleBot(app.config["TG_TOKEN"],threaded=False)
quart_url = Config.QUART_URL



# Process webhook calls
@app.route(app.config["WEBHOOK_URL_PATH"], methods=['POST'])
def webhook():
	if flask.request.headers.get('content-type') == 'application/json':
		json_string = flask.request.get_data().decode('utf-8')
		update = telebot.types.Update.de_json(json_string)
		bot.process_new_updates([update])
		return ''
	else:
		flask.abort(403)

# ==========================================================================================
# All tg message handler functions for will be placed BELOW


#handle start command
@bot.message_handler(commands=['start'])
def start_message(message):
	mongodb_query.new_user(message.chat.id)
	bot.send_message(message.chat.id, messages.greetingMessage)# прикрепляем клавиатуру к сообщению



#handler for all text messages with urls
@bot.message_handler(content_types=['text'])
def send_text(message):
	chat_id = message.chat.id

	quart_telethon = requests.post(url = quart_url+'/checkonegroup', json={"group": message.text})
	#return 200 if group and usr_list is accessible
	if quart_telethon.status_code == 200:
		mongodb_query.set_url(chat_id, message.text)
		bot.send_message(chat_id, messages.group_accepted, reply_markup = collect_data())
	elif quart_telethon.status_code == 204:
		bot.send_message(chat_id, messages.group_unreacheble, reply_markup = collect_data())
	else:
		bot.send_message(chat_id, messages.problems_with_sniffer)




# handle data from inline-keyboard
@bot.callback_query_handler(func=lambda message:True)
def answerOnInline(message):
	chat_id = message.message.chat.id

	if "analyze" in message.data:
		button = message.data.split('_')[1]
		#Очистить список добавленных групп
		if button == "0":
			mongodb_query.clear_urls(chat_id)
			bot.send_message(chat_id, messages.group_cleared)
		#Показать список добавленных групп
		elif button == "1":
			urls = mongodb_query.get_urls(chat_id)
			if urls:
				msg_urls = ''
				for url in urls:
					msg_urls += url + '\n'
				bot.send_message(chat_id, msg_urls, reply_markup = collect_data())
			else:
				bot.send_message(chat_id, messages.no_group_added, reply_markup = collect_data())
		#Приступить к анализу
		elif button == "2":
			urls = mongodb_query.get_urls(chat_id)
			analyse_urls(urls, chat_id)


# ==========================================================================================
# All inline-keyboards functions will be placed BELOW

def collect_data():
	keyboard = types.InlineKeyboardMarkup()
	keys = ['Очистить группы','Показать добавленные','Анализировать']
	for i in range(len(keys)):
		keyboard.add(types.InlineKeyboardButton(text=keys[i],callback_data="analyze_{0}".format(i)))
	return keyboard

# ==========================================================================================
# Analyze urls function

def analyse_urls(urls, chat_id):

	if not urls:
		bot.send_message(chat_id, messages.not_enought_groups)
	elif len(urls) > 1:
		dict_for_quart = {}
		for i in range(len(urls)):
			# {1: "group_url"}
			dict_for_quart[str(i)] = urls[i]
		bot.send_message(chat_id, messages.analyze_request_sent)
		quart_telethon = requests.post(url = quart_url+'/analyze', json={"to_analyze": dict_for_quart})
		#return json with user_data(str "name", str "nickname", list  "groups")
		if quart_telethon.status_code == 200:
			analyzed_users = ast.literal_eval(quart_telethon.text)
			output = ""
			for user_data in analyzed_users:
				print(user_data)
				#max limit of message 4096
				# check for 3500 is enought for our case
				if len(output) > 3500:
					bot.send_message(chat_id, output)
					output =  ""
				else:
					output +=  user_data["name"]+"(@"+user_data["nickname"]+") - "+str(user_data["groups"])+"\n"
			bot.send_message(chat_id, output)
			bot.send_message(chat_id, messages.low_pleasure)
			mongodb_query.clear_urls(chat_id)
		elif quart_telethon.status_code == 204:
			bot.send_message(chat_id, messages.not_enought_groups)
		elif quart_telethon.status_code == 209:
			#no matches
			bot.send_message(chat_id, messages.no_mathes)
	else:
		bot.send_message(chat_id, messages.no_group_added)

# ==========================================================================================
# SET WEBHOOK
try:
	# Remove webhook, it fails sometimes the set if there is a previous webhook
	bot.remove_webhook()
	time.sleep(5)
	bot.set_webhook(url=app.config["WEBHOOK_URL_BASE"] + app.config["WEBHOOK_URL_PATH"], certificate=open(app.config["WEBHOOK_SSL_CERT"], 'r'))
except Exception as e:
	print("couldnt set webhook, probably it wasn't removed")
	print(e)
