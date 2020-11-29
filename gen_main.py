import data_generator
import json
import sys
gen = data_generator.DataGenerator('fields.json')

suffix = str(0)
total = 5000000
data = []
for i in range(total+1):
    if i%10000 == 0 and i>2:
        with open('testfiles/testdata_'+suffix, 'a') as fh:
            json.dump(data, fh, indent=1)
        data = []
        suffix = str(i)
        print('{}%'.format(i/total * 100), end='\r')
        if i == total:
            break
    data.append(gen.generate())
    