from pymongo import MongoClient
from config import Config


client = MongoClient(Config.MONGO_URI)
db = client.localstore


# Creating new user with predefined field urls contaiins list
def new_user(chat_id):
    if not get_user(chat_id):
        db.sniff_users.insert({"chat_id": chat_id, "urls":[]})

    return True


# Creating if chat_id is new
def get_user(chat_id):
    if list(db.sniff_users.find({"chat_id": chat_id}).limit(1)):
        return True
    return False


# set or append new url
def set_url(chat_id, url):
    previous_urls = get_urls(chat_id)
    if previous_urls:
        previous_urls.append(url)
        db.sniff_users.update({"chat_id": chat_id},
                                {"$set": {
                                        "urls":previous_urls
                                        }
                                })
    else:
        db.sniff_users.update({"chat_id": chat_id},{"$set": {"urls": [url]}})
    return True


#returns list of urls
def get_urls(chat_id):
    usr_data = list(db.sniff_users.find({"chat_id": chat_id}).limit(1))
    if usr_data:
        if "urls" in usr_data[0]:
            return usr_data[0]["urls"]
    return False


#clear group urls
def clear_urls(chat_id):
    db.sniff_users.update({"chat_id": chat_id}, {"chat_id": chat_id, "urls":[]})
    return True
