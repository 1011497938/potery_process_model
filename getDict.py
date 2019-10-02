# coding:utf-8
import re
import sys
import time
import random
import traceback
import urllib.request
from urllib.parse import quote
import string
import json
import os


def download(url): 
    url = urllib.parse.quote(url, safe=string.printable)
    # print(url)
    response = urllib.request.urlopen(url)
    return response.read().decode('utf-8')


poem_dir = './data/poem/'
dict_dir = './data/dict/'

def craw(root_url):
    word2count = {}
    list = os.listdir(poem_dir) #列出文件夹下所有的目录与文件
    for i in range(0,len(list)):
        path = os.path.join(poem_dir,list[i])
        if os.path.isfile(path):
            # print(path)
            file = json.loads(open(path, 'r', encoding='utf-8').read())
            for poem_id in file:
                poem = file[poem_id]
                for shi_data in poem['ShiData']:
                    sentences = [sentence['Content']  for sentence in shi_data['Clauses']]
                    for word in ''.join(sentences):
                        if word not in word2count:
                            word2count[word] = 0
                        word2count[word] += 1
    words = [word for word in word2count if word2count[word]> 0]

    used_words = set(open(dict_dir + 'used_words' + '.csv', 'r', encoding='utf-8').read().strip('\n').split('\n'))
    word_dict = {}
    try_count = 0
    downLoadNum = 1
    total_num = len(words) - len(used_words)
    print('总数', total_num)
    while len(words)!=0:
        word = words.pop()
        if word in used_words:
            continue
        new_url = root_url + word
        # print(new_url)
        try:
            response = download(new_url)
            downLoadNum += 1
            print(downLoadNum, new_url)
            # print('response', response)
            used_words.add(word)
            if response=='抱歉，系统找不到该韵字。':
                print('抱歉，系统找不到该韵字。', word)
                continue
            word_dict[word] = json.loads(response)
            if downLoadNum%1000==0:
                print(downLoadNum, downLoadNum/total_num)
                # print('word_dict', word_dict)
                text = json.dumps(word_dict, ensure_ascii=False, sort_keys=True, indent=1)
                open(dict_dir + word + '.json', 'w', encoding='utf-8').write(text)
                word_dict = {}
                open(dict_dir + 'used_words' + '.csv', 'w', encoding='utf-8').write('\n'.join(used_words))
            try_count = 0
        except Exception:
            try_count += 1
            if try_count<10:
                words.append(word)
            else:
                try_count = 0
            traceback.print_exc()
            print('失败', new_url)

def data2dict():
    word2count = {}
    new_words = set()
    files = os.listdir(dict_dir) #列出文件夹下所有的目录与文件
    # print(files)

    for i in range(0,len(files)):
        path = os.path.join(dict_dir,files[i])
        # print(path)
        if '.json' in path:
            # print(path)
            # path = path.encode('utf-8')
            file = json.loads(open(path, 'r', encoding='utf-8').read())
            for word in file:
                content = file[word]
                if 'Allusions' in content:
                    allusions = content['Allusions']
                    for allusion in allusions:
                        for word in allusion.split(' '):
                            new_words.add(word)
                if 'Prewords' in content:
                    prewords = content['Prewords']
                    for preword in prewords:
                        for word in preword.split(' '):
                            new_words.add(word)
                if 'Sufwords' in content:
                    sufwords = content['Prewords']
                    for sufword in sufwords:
                        for word in sufword.split(' '):
                            new_words.add(word)
    print(len(new_words))
    open(dict_dir + 'new_words' + '.csv', 'w', encoding='utf-8').write('\n'.join(new_words))

if __name__=='__main__':
    print('目前系统的编码为：',sys.getdefaultencoding())
    root_url = 'https://api.sou-yun.cn/open/RhymeDictionary?id='
    craw(root_url)
    data2dict()
