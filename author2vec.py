from gensim.models import AuthorTopicModel
from gensim.corpora import mmcorpus
from gensim import corpora
from gensim.test.utils import common_dictionary, datapath, temporary_file
import json
from wordDiv import seg, segAll
import os

poem_dir = './data/poem/'
author_model_path = './model/author2vec/author2vec.model'

def train():
    author2doc = {}
    corpus = []
    count = 0
    files = os.listdir(poem_dir) #列出文件夹下所有的目录与文件
    for file in files:
        path = os.path.join(poem_dir,file)
        # if count>100 :
        #     break
        if os.path.isfile(path):
            # print(path)
            f = open(path, 'r', encoding='utf-8')
            file = json.loads(f.read())
            f.close()
            for poem_id in file:
                if count%100000==0 and count!=0:
                    print(count, len(corpus))
                poem = file[poem_id]
                # print(poem_id)
                for shi_data in poem['ShiData']:
                    author = shi_data['Author']
                    if author == '无名氏':
                        continue
                    sentences = [sentence['Content']  for sentence in shi_data['Clauses']]
                    content = ' '.join(sentences)
                    words = seg(content) #+ segAll(content)
                    # words = dictionary.doc2bow(words)
                    corpus.append(words)
                    if author not in author2doc:
                        author2doc[author] = []
                    author2doc[author].append(count)
                    count += 1
                    # print(count)
    dictionary = corpora.Dictionary(corpus)
    corpus = [dictionary.doc2bow(doc) for doc in corpus]
    print('开始训练', len(corpus), len(author2doc.keys()))
    model = AuthorTopicModel(corpus, author2doc=author2doc, id2word = dictionary, iterations=10)
    # model = AuthorTopicModel.load(author_model_path)
    # model.update(corpus, author2doc=author2doc,  iterations=10)
    model.save(author_model_path)

train()