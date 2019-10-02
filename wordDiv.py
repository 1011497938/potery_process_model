# -*- coding: UTF-8 -*- 
import re
import os
import jieba

poem_dir = './data/poem/'
dict_dir = './data/dict/'

new_words = open(dict_dir + 'new_words.csv', "r",encoding='utf-8').readlines()

for new_word in new_words:
    # print(place[0:-1])
    jieba.add_word(new_word)

stop_words = set(list('。，、＇：∶；?‘’“”〝〞ˆˇ﹕︰﹔﹖﹑·¨….¸;！´？！～—ˉ｜‖＂〃｀@﹫¡¿﹏﹋﹌︴々﹟#﹩$﹠&﹪%*﹡﹢﹦﹤‐￣¯―﹨ˆ˜﹍﹎+=<­­＿_-\ˇ~﹉﹊（）〈〉‹›﹛﹜『』〖〗［］《》〔〕{}「」【】︵︷︿︹︽_﹁﹃︻︶︸﹀︺︾ˉ﹂﹄︼'))
def filter(words):
    return [word for word in words if word not in stop_words]
    
def segAll(sentence):
    # list(jieba.cut(sentence, cut_all=True)) + 
    return filter(list(sentence))

def seg(sentence):
    return filter(list(jieba.cut(sentence)))


