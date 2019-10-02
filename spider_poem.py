# coding:utf-8
import re
import sys
import time
import random
import traceback
import urllib.request
import json

def download(url):
    response = urllib.request.urlopen(url)
    return response.read().decode('utf-8')


dir_name = 'data/poem/'
class SpiderMain(object):
    def craw(self, root_url):
        poem_dict = {}
        try_count = 0
        downLoadNum = 1
        total_num = 857304
        while downLoadNum<total_num:
            new_url = root_url + str(downLoadNum)
            downLoadNum += 1
            try:
                response = download(new_url)
                print(downLoadNum-1)
                # print(response)
                poem_dict[downLoadNum-1] = json.loads(response)
                if (downLoadNum-1)%100==0:
                    print(downLoadNum-1, downLoadNum-1/total_num)
                    text = json.dumps(poem_dict, ensure_ascii=False, sort_keys=True, indent=1)
                    open(dir_name + str(downLoadNum-1) + '.json', 'w', encoding='utf-8').write(text)
                    poem_dict = {}
                # time.sleep(0.1)
                # open(dir_name + str(downLoadNum-1) + '.xml', 'w', encoding='utf-8').write(response)
                try_count = 0
                # break
            except Exception:
                try_count += 1
                if try_count<10:
                    downLoadNum -= 1
                else:
                    try_count = 0
                traceback.print_exc()
                print('失败', new_url)


if __name__=='__main__':
    print('目前系统的编码为：',sys.getdefaultencoding())
    root_url = 'https://api.sou-yun.com/api/poem?jsontype=true&key='
    obj_spider = SpiderMain()
    obj_spider.craw(root_url)
