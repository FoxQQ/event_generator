import json
from pymongo import MongoClient
from pymongo.collection import Collection
db_name = 'test'
collection_name = 'testdata'
client = MongoClient('mongodb://db-host.local:27017')

db = client[db_name]

try:
    collection = Collection(db, collection_name, create=True)
except Exception as e:
    print(e)

collection = db[collection_name]

for suffix in range(20000,5000000,10000):
    try:
        with open('testfiles/testdata_'+str(suffix),'r') as  fh:
            data = json.load(fh)
            { item.update({'_id':item['vuln_hash']}) for item in data}
    except:
        continue
    it = 0
    batch = 10000
    while it < len(data):
        res = collection.insert_many(data[it:it+batch])
        it += batch
        print('{}/{} - {}'.format(it, len(data), suffix))

    # for i,item in enumerate(data):
    #     if i%1000 == 0:
    #         print(suffix, i)
    #     try:
    #         # collection_data_obj.insert(json.dumps(item))
            
#     #     except Exception as e:
#     #         pass
print('done')