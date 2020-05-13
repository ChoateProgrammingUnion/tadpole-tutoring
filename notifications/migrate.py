import json
import pymongo

filename = "times"

client = pymongo.MongoClient(host="mongodb+srv://ethanchapman:bTuczH2H4oeB4Cu1@tadpole-tutoring-0hxx5.mongodb.net/test?retryWrites=true&w=majority")
with open(filename + ".json") as f:
    data = list(json.load(f))
    for each_row in data:
        print(each_row)
        print(client['prod_database'][filename].insert_one(dict(each_row)))

