import pymongo
import datetime
import config
import notify


def poll(*null):
    email()


def email():
    client = pymongo.MongoClient(host=config.DB)

    sender = notify.Email()
    for each_notification in client['prod_database']['notifications'].find({"time": {"$lt": datetime.datetime.now()}, "sent": False}):
        email = each_notification.get('email')

        client['prod_database']['notifications'].update_one({"_id": each_notification.get("_id")}, {"$set": {"sent": True}})
        sender.send(email.get('address'), email.get('subject'), email.get('msg'), verbose=True)
