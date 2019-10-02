import json
import os
import copy
from commonFunction import writeJson, loadJson


poem_dir = './data/poem/'
potery_rank_path = './data/potery_rank.json'
p_id2rank = loadJson(potery_rank_path)

class Comments:
    def __init__(self, json_object, sentence):
        # print(json_object['Content'])
        try:
            self.content = json.loads(json_object['Content'])
        except:
            self.content = json_object['Content']

        self.index = json_object['Index']
        self.Type = json_object["Type"]  #WordDictInJson是json以外其他全是text
        self.sentence = sentence


class Author:
    def __init__(self, author_name):
        self.name = author_name

class Sentence:
    def  __init__(self, json_object, potery, index):
        if 'Content' in json_object:
            self.content = json_object['Content']
        else:
            self.content = ""

        if 'Comments' in json_object:
            self.comments = json_object['Comments']
        #     # if len(comments)>1:
        #     #     print(comments)
        #     self.comments = [commentManager.createComments(comment, self) for comment in comments]
        # else: 
        #     self.comments = []
        
        self.potery = potery
        self.index = index
        # BreakAfter 是什么

class Potery:
    def __init__(self, json_object):
        self.id = json_object["id"]
        shidata = json_object["ShiData"][0]

        if 'Author' in shidata:
            self.author = shidata['Author']
            if self.author == '无名氏':
                self.author = ''
        else:
            self.author = ''
        self.author = authorManager.createAuthor(self.author)

        self.sentences = [sentenceManager.createSentence(item, self, index) for index, item in enumerate(shidata['Clauses'])]

    def getVec128():
        return getPoteryVec128d(self.id)

    def getPageRank():
        if self.id in p_id2rank:
            return p_id2rank[self.id] 
        else:
            print(self.id, '没有pagerank!')
            return -999

    def getSimpJson(self):
        return {
            # 'id': self.id,
            'author': self.author.name,
            'sentence': [sentence.content  for sentence in self.sentences]
        }

    
class CommentManager:
    def __init__(self):
        self.comments = set()
    def createComments(self, json_object, sentence):
        # new_comment = Comments(json_object, sentence)
        # self.comments.add(new_comment)

        # 防止爆掉直接用dict吧
        new_comment = {}
        if json_object["Type"]=='WordDictInJson':
            new_comment['content'] = json.loads(json_object['Content'])
        else:
            new_comment['content']= json_object['Content']
        new_comment['index'] = json_object['Index']
        new_comment['type'] = json_object["Type"]  #WordDictInJson是json以外其他全是text
        new_comment['sentence'] = sentence

        return new_comment

class SentenceManager: 
    def __init__(self):
        self.sentences = set()
        self.auto_id = 0
    def createSentence(self, json_object, potery, index):
        new_sentence = Sentence(json_object, potery, index)
        new_sentence.id = 's_' + str(self.auto_id)
        self.sentences.add(new_sentence)
        return new_sentence

class AuthorManager:
    def __init__(self):
        self.name2author = {}
    def createAuthor(self, name):
        if name in self.name2author:
            return self.name2author[name]
        else:
            new_author = Author(name)
            self.name2author[name] = new_author
            return new_author

class PoteryManager:
    def __init__(self):
        self.id2potery = {}
        self.poteries = []
        self.loads()

    def getAllPoteries(self):
        return list(self.poteries)

    def getAllIds(self):
        return [potery.id for potery in self.poteries]

    def getImpPotery(self, num):
        return self.poteries[0:num]

    def loads(self):
        files = os.listdir(poem_dir) #列出文件夹下所有的目录与文件
        count = 0
        for file in files:
            path = os.path.join(poem_dir,file)
            if os.path.isfile(path):
                file = loadJson(path)
                for potery_id in file:
                    file[potery_id]['id'] =   + potery_id
                    self.createPotery(file[potery_id])
                    count += 1
                    if count%100000==0:
                        print(count)
        self.poteries = sorted(self.poteries, key=lambda potery: potery.id)
        print('加载完成')
        
    def createPotery(self, json_object): 
        new_potery = Potery(json_object)
        self.id2potery[json_object['id']] = new_potery
        self.poteries.append(new_potery)
        return new_potery


authorManager = AuthorManager()
commentManager = CommentManager()
sentenceManager = SentenceManager()
poteryManager = PoteryManager()

def getId2simpPotery():
    result = {potery.id: potery.getSimpJson()  for potery in poteryManager.poteries}
    writeJson('simp_potery',result)

def getId2PoteryName():
    result = {potery.id: potery.sentences[0].content for potery in poteryManager.poteries}
    writeJson('id2potery_name',result)

# getId2PoteryName()