from wordDiv import seg, segAll
import gensim
from multiprocessing import cpu_count
import json
import os
from sklearn.manifold import TSNE

model_path = './model/word2vec/word2vec.model'
poem_dir = './data/poem/'
dict_dir = './data/dict/'
word2count_path = './data/word2count.json'
vec3d_path = './data/word_vec3d.json'

model = None
word2count = json.loads(open(word2count_path, 'r', encoding='utf-8').read())

def train():
    global model
    files = os.listdir(poem_dir) #列出文件夹下所有的目录与文件
    corups = []
    word2count = {}

    count = 0
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
                    shi = []
                    shi_chars = []
                    for sentence in sentences:
                        words = seg(sentence)
                        chars = segAll(sentence)
                        # print(sentence, ' '.join(words))
                        corups.append(words)
                        corups.append(chars)
                        shi += words
                        shi_chars += chars
                        # for word in words:
                        #     if word not in word2count:
                        #         word2count[word] = 0
                        #     word2count[word] +=  1
                    corups.append(shi)
                    corups.append(shi_chars)

    # open(word2count_path, 'w', encoding='utf-8').write(json.dumps(word2count, ensure_ascii=False, sort_keys=True, indent=1))

    print('开始训练',len(corups))
    # print(corups[0:100])
    model = gensim.models.Word2Vec.load(model_path)
    # model = gensim.models.Word2Vec(corups, workers=cpu_count(), size=124, window=5, min_count=20)
    model.train(corups, total_examples=len(corups), epochs=10)
    model.save(model_path)
    print('保存成功', len(model.wv.vocab))
    return model

def load():
    global model
    if model is None:
        print('加载word2vec模型')
        model = gensim.models.Word2Vec.load(model_path)
    return model

def getVec(word):
    model = load()
    wv = model.wv
    return wv[word]

def getAllVec():
    model = load()
    wv = model.wv
    return [wv[key] for key in wv.vocab]

def vec23D():
    model = load()
    wv = model.wv
    vecs = getAllVec()
    print('开始计算TSNE')
    tsne=TSNE(n_components=3, n_iter=250, learning_rate=200)
    result =  tsne.fit_transform(vecs)  #进行数据降维,降成两维
    word2vec = {word: result[index].tolist()  for index, word in enumerate(wv.vocab)}
    print('TSNE计算成功')
    open(vec3d_path, 'w', encoding='utf-8').write(json.dumps(word2vec, ensure_ascii=False, sort_keys=True, indent=1))
    return result

def testSimlar():
    model = load()
    wv = model.wv

    for word in wv.vocab:
        r = wv.most_similar(word)
        print(word, r)


if __name__ == "__main__":
    # train()
    # vec23D()
    testSimlar()
    pass

