import json
import os
import copy
from gensim.models.doc2vec import Doc2Vec
from commonFunction import writeJson, loadJson
from dataStore import poteryManager, sentenceManager

potery_rank_path = './data/potery_rank.json'

all_ids = None
def getAllIds():
    global all_ids
    if all_ids is not None:
        return list(all_ids)
    ids = [potery.id for potery in poteryManager.poteries]
    ids = sorted(ids, key=lambda poem_id: poem_id)
    all_ids = ids #[0:100]
    return list(all_ids)

imp_ids = None
def getImpIds(num=10000):
    global imp_ids
    if imp_ids is not None:
        return list(imp_ids)

    ids = getAllIds()
    potery_rank = loadJson(potery_rank_path)
    def getRank(_id):
        if _id in potery_rank:
            return potery_rank[_id]
        else:
            return -999
    ids = sorted(ids, key=lambda _id: getRank(_id), reverse=True)
    imp_ids = ids[0:num]
    return list(imp_ids)

model_128d = None

def getPoteryVec128d(_id):
    global model_128d
    # vec_size = 128
    if model_128d is None:
        potery_model_path = './model/potery2vec/128d/potery2vec_128d.model'
        model_128d = Doc2Vec.load(potery_model_path)
    docvecs = model_128d.docvecs
    if _id in docvecs:
        return docvecs[_id]
    else:
        print(_id, '这首词没有向量')