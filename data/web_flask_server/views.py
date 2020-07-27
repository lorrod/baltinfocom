""" Views file """

import os
import ast
from app import app
from config import Config
from subprocess import Popen, PIPE
import requests
from flask import Flask, flash, redirect, render_template, url_for, jsonify, request


quart_url = Config.QUART_URL

# main page
@app.route('/', methods=['GET', 'POST'])
def main():
	error = request.args.get('error')
	# check if telethon is authorized
	quart_auth = requests.post(url = quart_url+'/auth')
	category = "group"
	if quart_auth.status_code == 203:
		# if so, then the button <auth> will shown on page
		category = "no_auth"
	if error:
		flash(error, category)
	return render_template('main.html', title='Главная страница')

#function for receiving telegram code and then try to auth with telethon
@app.route('/auth', methods=['POST'])
def root():
	passwd = request.get_json()
	if passwd:
		quart_auth = requests.post(url = quart_url+'/auth', json = passwd)
	else:
		quart_auth = requests.post(url = quart_url+'/auth')
	#203 not authorized -> send telegram code to me -> open modal for you
	#200 already auth#
	return "auth_info", quart_auth.status_code

# here could be analyzed json in future
# now just checking telethon connection
@app.route('/analyze', methods=['POST'])
def analyze():
	information = request.get_json()
	# check if telethon is authorized
	quart_auth = requests.get(url = quart_url+'/auth')

	if quart_auth.status_code == 200:
		return redirect(url_for('output', title='Результат', url=information))
	elif quart_auth.status_code == 203:
		return redirect(url_for("main", error="Необходимо авторизироваться"))

# take dict from url (ex. {"1":"telegram_group_url", ...})
@app.route('/output', methods=['GET'])
def output():
	try:
		dict_urls = ast.literal_eval(request.args.get('url'))

		quart_telethon = requests.post(url = quart_url+'/analyze', json={"to_analyze": dict_urls})
		if quart_telethon.status_code == 200:
			return render_template('output.html',user_matches = quart_telethon.json())
		elif quart_telethon.status_code == 204:
			return redirect(url_for("main", error = "Не хватает групп для сравнения! Возможно url введен неверно или просмотр участников запрещен :("))
		elif quart_telethon.status_code == 209:
			#no matches
			return redirect(url_for("main", error = "Нету совпадений"))
	except ValueError:
		return redirect(url_for("main", error = "Неверный запрос!"))



# ==========================================================================================
# All functions for testing will be placed BELOW
