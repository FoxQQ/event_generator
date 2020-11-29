import json
import os
import time
import random
class DataGenerator:
    def __init__(self, template_path):
        if not template_path:
            raise ValueError('data template_path required!')

        if not os.path.isfile(template_path):
            raise ValueError('template_path is not existing')

        self.template = self._load_template(template_path)
        print(self.template)
        print(','.join(self.template.keys()))

    def _load_template(self, template_path):
        with open(template_path, 'r') as fh:
            return json.load(fh)

    def generate(self):
        data = {}

        for k,v in self.template.items():
            v_type = v.get('type')
            if v_type == 'datetime':
                data[k] = round(time.time(), 0)
            elif v_type == 'int':
                if v.get('values'):
                    min_ = v.get('values').get('min')
                    max_ = v.get('values').get('max')
                else:
                    min_, max_ = 0, 10
                data[k] = random.randint(min_, max_)
            elif v_type == 'string':
                if v.get('length'):
                    length = int(v.get('length'))
                else:
                    length = 19
                data[k] = str(''.join([ chr(random.randint(65,85)) for i in range(length) ]))
            elif v_type == 'ipv4':
                data[k] = '{}.{}.{}.{}'.format(random.randint(0,255), random.randint(0,255),random.randint(0,255),random.randint(0,255))

        return data
