# coding:utf-8
import re
import sys
import time
import random
import traceback
import urllib.request
import json
from urllib.parse import quote
import string
from opencc import OpenCC 
import threading
import time

# 繁体转简体
cc = OpenCC('s2t')
print('加载繁体->简体转换器')
def s2t(string):
	return cc.convert(string)

def download(url):
    url = quote(url,safe=string.printable)
    response = urllib.request.urlopen(url, timeout=30)
    return response.read().decode('utf-8')


dir_path = 'data/poets/poet_info.json'
threading_num = 0
class SpiderMain(object):
    def craw(self, root_url):
        global threading_num
        poet_dict = open(dir_path, 'r', encoding='utf-8').read()
        poet_dict = json.loads(poet_dict)
        poets = open('./data/author_list.csv', 'r', encoding='utf-8').readlines()

        def downloadPoetInfo():
            global threading_num
            poet_name = poets.pop()
            poet_name = s2t(poet_name).strip('\n')
            if poet_name in poet_dict:
                threading_num -= 1
                return
            new_url = root_url + str(poet_name) + '&o=json'
            try:
                response = download(new_url)
                downLoadNum = len(poet_dict.keys())
                print(downLoadNum, poet_name)
                poet_dict[poet_name] = json.loads(response) 
                if (downLoadNum-1)%100==0:
                    text = json.dumps(poet_dict, ensure_ascii=False, sort_keys=True, indent=1)
                    open(dir_path, 'w', encoding='utf-8').write(text)
                threading_num -= 1
            except Exception:
                threading_num -= 1
                print('失败', new_url)
                
        while len(poets)!=0:
            if threading_num<20:
                # print(threading_num)
                threading_num += 1
                t = threading.Thread(target=downloadPoetInfo, args=())
                t.start()
            time.sleep(1)

        text = json.dumps(poet_dict, ensure_ascii=False, sort_keys=True, indent=1)
        open(dir_path, 'w', encoding='utf-8').write(text)

if __name__=='__main__':
    print('目前系统的编码为：',sys.getdefaultencoding())
    root_url = 'https://cbdb.fas.harvard.edu/cbdbapi/person.php?name='
    obj_spider = SpiderMain()
    obj_spider.craw(root_url)
