from telethon import TelegramClient, sync, errors
from config import Config
import sys



api_id = Config.TG_API_ID
api_hash = Config.TG_API_HASH

client = TelegramClient('sniffer_tool', api_id, api_hash).start()


#Возвращает
def get_channel(url):
	try:
		channel = client.get_entity(url)
		return channel
	except ValueError:
		# no channel by input url
		return False


# Возвращает ключ url и массив с данными о подписчиках
# пример: {"channel_url" : [ {"name":"", "nickname":"","id":""},..] }
# если скрыты пользователи -- False
def get_users(channel):
	user_list = []
	try:
		for user in client.get_participants(channel):
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


"""
channels_data = [
					{"first" : [ {"name":"", "nickname":"","id":""},..] }
					{"second" : [ {"name":"", "nickname":"","id":""},..] }
				]
"""
def compare_groups(channels_data):
	dict_keys = list(channels_data.keys())
	output = []
	#  если чел в 2 и 3 группе, то найден не будет
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
	#		{"name":"", "nickname":"","id":"",groups:["url","url2"]}
	return output



def run_list(list_urls):
	channels_data = {}
	for url in list_urls:
		channel = get_channel(url)
		if channel:
			channel_dict = get_users(channel)
			if channel_dict:
				channels_data[url] = channel_dict

		else:
			print("Группа не найдена: "+url)
	if len(channels_data) > 1:
		return compare_groups(channels_data)
	else:
		return "Не хватает групп для сравнения"



#example args: https://t.me/leadersofdigital greedygame
if __name__ == "__main__":
	if len(sys.argv) > 2:
		result = run_list(sys.argv[1:])
		print(result)
	else:
		print("Для сравнения требуется минимум 2 группы")
