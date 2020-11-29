import json
from splunklib.client import connect

collection_name = 'testdata'
s = connect(host='ubunt2.local', username='admin', password='1234qwer',
            owner='nobody',app='search')
print('Kvstore list:')
print([item.name for item in s.kvstore.list()])
try:
    s.kvstore.create(name=collection_name)
except:
    pass

collection_data_obj = [item for item in s.kvstore.list() if item.name == collection_name][0].data
print(collection_data_obj)

# docs = [{'_key':'3','k':'v'},{'_key':'4','k':'v'}]
# print(*docs)
# collection_data_obj.batch_save(*docs)


for suffix in range(0,5000000,10000):
    try:
        with open('testfiles/testdata_'+str(suffix),'r') as  fh:
            data = json.load(fh)
            { item.update({'_key':item['vuln_hash']}) for item in data}
    except:
        continue
    it = 0
    batch = 1000
    while it < len(data):
        res = collection_data_obj.batch_save(*data[it: it+batch])
        it += batch
        print('{}/{} - {}'.format(it, len(data), suffix))

    # for i,item in enumerate(data):
    #     if i%1000 == 0:
    #         print(suffix, i)
    #     try:
    #         # collection_data_obj.insert(json.dumps(item))
            
    #     except Exception as e:
    #         pass
print('done')