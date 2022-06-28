import requests
import json
from ..app.database import BaseDb
path = '../../rulespider/result.out'
post_url = 'http://127.0.0.1:5000/db/testMongoWrite'

# with open(path, 'r', encoding='utf-8') as f:
#     for i in f:
#         data = json.loads(i.strip())
#         requests.post(post_url, json=data).json()

if __name__=="__main__":
    BaseDb= BaseDb()
    res = BaseDb.get_setdiff('test', 'app_info')
    print(res)