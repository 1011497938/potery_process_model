from wordDiv import seg, segAll
import gensim
from multiprocessing import cpu_count
import json
import os
from sklearn.manifold import TSNE
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from gensim.test.utils import common_texts
import networkx as nx 
import numpy as np
import traceback 
from dataStore import poteryManager, sentenceManager

potery_model_path = './model/potery2vec/3d/potery2vec_3d.model'
sentence_model_path = './model/sentence2vec/sentence2vec.model'

potery_rank_path = './data/potery_rank.json'

vec_size = 3

def potery2vec():
    documents = []
    count = 0
    files = os.listdir(poem_dir) #列出文件夹下所有的目录与文件
    for file in files:
        path = os.path.join(poem_dir,file)
        if os.path.isfile(path):
            # print(path)
            f = open(path, 'r', encoding='utf-8')
            file = json.loads(f.read())
            f.close()
            for poem_id in file:
                if count%100000==0:
                    print(count, len(documents))
                count += 1
                poem = file[poem_id]
                # print(poem_id)
                for shi_data in poem['ShiData']:
                    sentences = [sentence['Content']  for sentence in shi_data['Clauses']]
                    content = ' '.join(sentences)
                    documents.append(TaggedDocument(seg(content) + segAll(content), [poem_id]))
                    # print(poem_id)
        # if count>100:
        #     break
    print('开始计算')
    # model = Doc2Vec.load(potery_model_path)
    model = Doc2Vec(documents, vector_size=vec_size, window=5, min_count=10, workers=cpu_count())
    model.train(documents, total_examples=len(documents), epochs=20)
    model.save(potery_model_path)
    print('保存模型')

def pageRankPotery():
    G = nx.Graph()
    model = Doc2Vec.load(potery_model_path)
    wv = model.wv
    docvecs = model.docvecs

    poem_ids = []
    count = 0
    files = os.listdir(poem_dir) #列出文件夹下所有的目录与文件
    for file in files:
        path = os.path.join(poem_dir,file)
        if os.path.isfile(path):
            # print(path)
            file = json.loads(open(path, 'r', encoding='utf-8').read())
            for poem_id in file:
                if count%10000==0:
                    print(count, len(G.nodes))
                # print(count)
                count += 1
                # print(docvecs[poem_id].tolist())
                if poem_id in docvecs:
                    r = model.docvecs.most_similar([poem_id], topn=20)
                    # print(r)
                    for sim_id, sim in r:
                        if sim>0.50:
                            G.add_weighted_edges_from([(poem_id, sim_id, sim)])

    potery_rank = {}
    # print(len(G.nodes))
    print('开始计算page rank')
    pr=nx.pagerank(G, weight='weight', max_iter=1000)
    ranks = np.array([pr[person_id] for person_id in pr])
    print('计算结束')
    max = np.max(ranks)
    min = np.min(ranks)

    for potery_id in pr:
        rank = pr[potery_id]
        rank = (rank-min)/(max-min)
        potery_rank[potery_id] = rank
    open(potery_rank_path, 'w', encoding='utf-8').write(json.dumps(potery_rank, ensure_ascii=False, sort_keys=True, indent=1))
    return

def sentence2vec():
    documents = []
    count = 0
    files = os.listdir(poem_dir) #列出文件夹下所有的目录与文件
    for file in files:
        path = os.path.join(poem_dir,file)
        if os.path.isfile(path):
            # print(path)
            file = json.loads(open(path, 'r', encoding='utf-8').read())
            for poem_id in file:
                if count%100000==0:
                    print(count, len(documents))
                count += 1
                poem = file[poem_id]
                for shi_data in poem['ShiData']:
                    sentences = [sentence['Content']  for sentence in shi_data['Clauses']]
                    for index, sentence in enumerate(sentences):
                        sentence_id = poem_id + ',' + str(index)
                        documents.append(TaggedDocument(seg(sentence) + segAll(sentence), [sentence_id]))

    print('开始计算')
    model = Doc2Vec(documents, vector_size=vec_size, window=5, min_count=10, workers=cpu_count())
    model.train(documents, total_examples=len(documents), epochs=20)
    model.save(sentence_model_path)
    print('保存模型')

def potery23d():
    potery_rank = json.loads(open(potery_rank_path, 'r', encoding='utf-8').read())

    model = Doc2Vec.load(potery_model_path)
    wv = model.wv
    docvecs = model.docvecs

    poem_ids = []
    files = os.listdir(poem_dir) #列出文件夹下所有的目录与文件
    for file in files:
        path = os.path.join(poem_dir,file)
        if os.path.isfile(path):
            # print(path)
            file = json.loads(open(path, 'r', encoding='utf-8').read())
            for poem_id in file:
                if poem_id in docvecs:
                    # vecs.append(docvecs[poem_id])
                    poem_ids.append(poem_id)

    def getPoteryRank(poem_id):
        if poem_id in potery_rank:
            return potery_rank[poem_id]
        return 0
    for index in range(0, 900000):
        index = str(index)
        if index not in potery_rank:
            potery_rank[index] = 0

    sorted(poem_ids, key=lambda poem_id: potery_rank[poem_id]).reverse()
    poem_ids = poem_ids[: 10000] 

    print(len(poem_ids) ,'开始计算TSNE')
    vecs = [docvecs[poem_id] for poem_id in poem_ids]
    tsne=TSNE(n_components=2, n_iter=2000, learning_rate=1000, perplexity=50, verbose=1)
    result = tsne.fit_transform(vecs)  #进行数据降维,降成两维
    word2vec = {id: result[index].tolist()  for index, id in enumerate(poem_ids)}
    print('TSNE计算成功')
    open(potery2vec_path, 'w', encoding='utf-8').write(json.dumps(word2vec, ensure_ascii=False, sort_keys=True, indent=1))
    # open('./data/test.csv', 'w', encoding='utf-8').write('\n'.join(['\t'.join([str(vec) for vec in docvecs[poem_id].tolist()]) for poem_id in poem_ids]))
    # return result

def sentence23d():
    model = Doc2Vec.load(sentence_model_path)
    wv = model.wv
    docvecs = model.docvecs

    word2vec = {}
    vecs = []
    sentence_ids = []
    files = os.listdir(poem_dir) #列出文件夹下所有的目录与文件
    for file in files:
        path = os.path.join(poem_dir,file)
        if os.path.isfile(path):
            # print(path)
            file = json.loads(open(path, 'r', encoding='utf-8').read())
            for poem_id in file:
                poem = file[poem_id]
                for shi_data in poem['ShiData']:
                    sentences = [sentence['Content']  for sentence in shi_data['Clauses']]
                    for index, sentence in enumerate(sentences):
                        sentence_id =  poem_id + ',' + str(index)
                        if sentence_id in docvecs:
                            vecs.append(docvecs[sentence_id])
                            sentence_ids.append(sentence_id)
                            # print(docvecs[sentence_ids])
                            word2vec[sentence_id] = docvecs[sentence_id].tolist()

    print('开始计算TSNE')
    tsne=TSNE(n_components=3, n_iter=250, learning_rate=100)
    result =  tsne.fit_transform(vecs)  #进行数据降维,降成两维
    word2vec = {id: result[index].tolist()  for index, id in enumerate(sentence_ids)}
    print('TSNE计算成功')
    open(sentence2vec_path, 'w', encoding='utf-8').write(json.dumps(word2vec, ensure_ascii=False, sort_keys=True, indent=1))
    # return result


potery2content = {}
model = Doc2Vec.load(potery_model_path)
def loadPoterys():
    global potery2content
    documents = []
    count = 0
    files = os.listdir(poem_dir) #列出文件夹下所有的目录与文件
    for file in files:
        path = os.path.join(poem_dir,file)
        if os.path.isfile(path):
            # print(path)
            file = json.loads(open(path, 'r', encoding='utf-8').read())
            for poem_id in file:
                if count%100000==0:
                    print(count, len(documents))
                count += 1
                poem = file[poem_id]
                # print(poem_id)
                for shi_data in poem['ShiData']:
                    sentences = [sentence['Content']  for sentence in shi_data['Clauses']]
                    content = ' '.join(sentences)
                    potery2content[poem_id] = content

def getSim(poem_id):
    global potery2content, model
    sims = model.docvecs.most_similar([poem_id], topn=20)
    print(potery2content[poem_id])
    for id, sim in sims:
        print(potery2content[id], sim)
    print('\n\n\n')
if __name__ == "__main__":
    potery2vec()
    # potery23d()
    # pageRankPotery()
    # sentence2vec()
    # sentence23d()

    # loadPoterys()
    # getSim('352030')
    # getSim('164609')
    # getSim('69167')
    
    
