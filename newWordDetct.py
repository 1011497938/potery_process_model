# -*- coding: UTF-8 -*- 
# from __future__ import unicode_literals
from pynlpir import nlpir
import pynlpir
import sys
import codecs
import os
import json
#python2.7

new_word_path = './data/new_words.csv'
poem_dir = './data/poem/'

count = 0
text = ''
files = os.listdir(poem_dir) #列出文件夹下所有的目录与文件
corups = []
for file in files:
    path = os.path.join(poem_dir,file)
    if os.path.isfile(path):
        # print(path)
        file = json.loads(open(path, 'r', encoding='utf-8').read())
        for poem_id in file:
            if count%100000==0:
                print(count, len(corups))
            count += 1
            poem = file[poem_id]
            for shi_data in poem['ShiData']:
                sentences = [sentence['Content']  for sentence in shi_data['Clauses']]
                text += '\n'.join(sentences)
    break
pynlpir.open(encoding='utf_8')
temp_path = r'./data/temp.txt' 
open(temp_path, 'w', encoding='utf-8').write(text)
r = nlpir.GetFileNewWords(temp_path, 50000, True)
open(new_word_path,"w").write(str(r))
