from config import Config

import base64
import os
import json

import hypercorn.asyncio
from quart import Quart, render_template_string, request, jsonify, Response

from telethon import TelegramClient, utils, errors, connection




# ==========================================================================================
# Initializing


quart_cfg = hypercorn.Config()
quart_cfg.bind = ["0.0.0.0:8000"]

# Session name, API ID and hash to use
SESSION = "quart_telethon"
API_ID = Config.TG_API_ID
API_HASH = Config.TG_API_HASH


client = TelegramClient(SESSION,
						API_ID,
						API_HASH,
						connection=connection.ConnectionTcpMTProxyRandomizedIntermediate,
						 proxy=(Config.PROXY_MTP_URL, Config.PROXY_MTP_PORT, Config.PROXY_MT_SECRET))


phone = Config.phone

# Quart app
app = Quart(__name__)
app.secret_key = 'very_secret_ksasdfg'




# ==========================================================================================
# All telethon functions will be placed BELOW




# returns class with channel information
async def get_channel(url):
	try:
		channel = await client.get_entity(url)
		return channel
	except ValueError:
		# no channel by input url
		return False
	except ConnectionError:
		print("MTPROTO connection was broken! Reload server!")
		return False


#Get users from group
# input group telethon class
# returns  {"channel_url" : [ {"name":"", "nickname":""},..] }
# or False
async def get_users(channel):
	user_list = []
	try:
		for user in await client.get_participants(channel):
			user_dict = {}
			if user.last_name != None and user.first_name != None:
				user_dict["name"] = user.last_name+' '+user.first_name
			elif user.last_name != None:
				user_dict["name"] = user.last_name
			elif user.first_name != None:
				user_dict["name"] = user.first_name
			else:
				user_dict["name"] = "None("+str(user.id)+")"
			user_dict["nickname"] = user.username
			user_dict["id"] = user.id
			user_list.append(user_dict)
		return user_list
	except errors.rpcerrorlist.ChatAdminRequiredError:
		# Просмотр участников чата запрещен
		return False


# Compare users from different groups
# input dict {"url1": [{users_data["name"], users_data["nickname"], users_data["id"]},..],..}
# returns list [{"name":"", "nickname":"","id":"",groups:["url","url2"]},...]
def compare_groups(channels_data):
	dict_keys = list(channels_data.keys())
	output = []
	for url_key_num in range(len(dict_keys)):
		for user_data in channels_data[dict_keys[url_key_num]]:
			#создаем ключ у каждого пользователя с url паблика
			user_data["groups"] = [dict_keys[url_key_num]]
			# проверка есть ли еще группы для проверки
			if url_key_num + 1 < len(dict_keys):
				for i in range(url_key_num+1, len(dict_keys)):
					# проверям есть ли в другой группе данный пользователь
					if user_data["id"] in [x['id'] for x in channels_data[dict_keys[i]]]:
						user_data["groups"].append(dict_keys[i])
			#тк user_data было проверено для всех групп
			# во избежании повторных проверок удаляем user_data
			if len(user_data["groups"]) != 1:
				output.append(user_data.copy())
				for group in user_data["groups"]:
					if group != dict_keys[url_key_num]:
						del_patt = user_data.copy().pop("groups")
						try:
							channels_data[group].remove(del_patt)
						except ValueError:
							#уже было удалено
							pass
	# возвращает массив с пользовательскими данными,
	#		где найдено 2 и более вхождений
	#		[{"name":"", "nickname":"","id":"",groups:["url","url2"]},...]
	if len(output) == 0:
		output.append("no_mathes")
	return output



# start analyzing from here, with functions: 	- get_channel
#												- get_users
#												- compare_groups
# input  {"1":"https://t.me/leadersofdigital", "2": "greedygame"}
# if success returns [{"name":"", "nickname":"","id":"",groups:["url","url2"]},...]
async def analyze(dict_urls):
	channels_data = {}
	for key in dict_urls:
		channel = await get_channel(dict_urls[key])
		if channel:
			channel_dict = await get_users(channel)
			if channel_dict:
				channels_data[dict_urls[key]] = channel_dict

			else:
				print("Группа не найдена: "+dict_urls[key])
	if len(channels_data) > 1:
		return compare_groups(channels_data)
	else:
		#"Не хватает групп для сравнения"
		return False



# ==========================================================================================
# All Quart url handlers functions for will be placed BELOW



# Connect the client before we start serving with Quart
@app.before_serving
async def startup():
	await client.connect()


# After we're done serving (near shutdown), clean up the client
@app.after_serving
async def cleanup():
	await client.disconnect()



@app.route('/auth', methods=['GET', 'POST'])
async def root():
	if request.method == "POST":

		# Check auth
		if await client.is_user_authorized():
			return "already_auth", 200

		# Check received parameters (code)
		info = await request.get_json()
		if info:
			if "code" in info:
				await client.sign_in(code=info["code"])
				return "logged in", 201
		else:
			# send code to me
			await client.send_code_request(phone)
		return "not_auth", 203



	if request.method == "GET":
		# If we're logged in send 200OK
		if await client.is_user_authorized():
			return "logged", 200
		# We're not logged in, so ask for the code
		return "not_logged", 203



@app.route('/analyze', methods=['POST'])
async def handle_analyze():
	#wait for {"1":"https://t.me/leadersofdigital", "2": "greedygame"}
	information = await request.get_json()
	if information["to_analyze"]:
		output = await analyze(information["to_analyze"])
		print(output)
		if output and output != "no_mathes":
			return json.dumps(output)
		elif output == "no_mathes":
			return "no_mathes", 209
		else:
			# no group to compare
			return "no_group_compare", 204
	else:
		return "bad_json", 400


#uses from telegramBot
@app.route('/checkonegroup', methods=['POST'])
async def handle_check():
	#wait for {"group":"https://t.me/leadersofdigital"}
	information = await request.get_json()
	if information["group"]:
		output = await get_channel(information["group"])
		if output:
			return "alright", 200
		else:
			# no group or user list forbidden
			return "no_group_compare", 204
	else:
		return "bad_json", 400

async def main():
	await hypercorn.asyncio.serve(app,quart_cfg)


# By default, `Quart.run` uses `asyncio.run()`, which creates a new asyncio
# event loop. If we create the `TelegramClient` before, `telethon` will
# use `asyncio.get_event_loop()`, which is the implicit loop in the main
# thread. These two loops are different, and it won't work.
#
# So, we have to manually pass the same `loop` to both applications to
# make 100% sure it works and to avoid headaches.
#
# To run Quart inside `async def`, we must use `hypercorn.asyncio.serve()`
# directly.
#
# This example creates a global client outside of Quart handlers.
# If you create the client inside the handlers (common case), you
# won't have to worry about any of this, but it's still good to be
# explicit about the event loop.
if __name__ == '__main__':
	client.loop.run_until_complete(main())
