# # # 分类诗歌
# from wordDiv import seg, segAll
from getPotery import getAllIds, getImpIds
from commonFunction import writeJson, loadJson

import gensim
from multiprocessing import cpu_count
import json
import os
from sklearn.manifold import TSNE
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
import networkx as nx 
import numpy as np
import traceback

import pandas as pd
import matplotlib.pyplot as plt
from scipy.spatial.distance import pdist,squareform
from scipy.cluster.hierarchy import linkage, distance
from scipy.cluster.hierarchy import dendrogram
from sklearn.cluster import AgglomerativeClustering
from  sklearn.neighbors import kneighbors_graph
from sklearn.datasets import make_blobs
import matplotlib.pyplot as plt

imp_ids_num = 10000
potery_model_path = './model/potery2vec/128d/potery2vec_128d.model'
poem_dir = './data/poem/'
tree_path = './data/potery_tree_' + str(imp_ids_num) + '.json'
# ids2sim_imp_path = './data/诗词分 类，基于一万.json'

model = Doc2Vec.load(potery_model_path)
docvecs = model.docvecs

def getImpCat():
    vecs = []

    ids = getImpIds(imp_ids_num) #getAllIds()

    for _id in ids:
        vecs.append(docvecs[_id])

    print(len(vecs), len(vecs[0]))
    # print(points)
    disMat =  distance.pdist(vecs,'euclidean') 

    #define the linkage_matrix using ward clustering pre-computed distances 
    print('开始计算')
    linkage_matrix= linkage(disMat, method ='ward', optimal_ordering=True) #optonal :average ward etc

    def getTree(linkage_matrix):
        class TreeNode(object):
            def __init__(self, _id):
                self.id = _id
                self.parent = None
                self.childs = set()
                self.child_num = 0

        class NodeCompany():
            def __init__(self):
                self.id2node = {}
            def get(self, _id):
                id2node = self.id2node
                if _id in id2node:
                    return  id2node[_id]
                else:
                    id2node[_id] = TreeNode(_id)
                    return id2node[_id] 
        nodeCompany = NodeCompany()
        linkage_matrix = linkage_matrix.tolist()
        # print(linkage_matrix)

        for item in linkage_matrix:
            node1 = int(item[0])
            node2 = int(item[1])
            # sim = item[2]
            num = int(item[3])
            item[0] = node1
            item[1] = node2
            item[3] = num
    
        l_length = imp_ids_num
        for index,item in enumerate(linkage_matrix):
            child_num = item[3]
            node1 = nodeCompany.get(item[0])
            node2 = nodeCompany.get(item[1])
            index += l_length
            parent_node = nodeCompany.get(index)
            node1.parent = parent_node
            node2.parent = parent_node
            parent_node.childs.add(node1)
            parent_node.childs.add(node2)
            parent_node.child_num = child_num
        id2node = nodeCompany.id2node
        # for key in id2node:
        #     node = id2node[key]
            # print([sub.id for sub in node.childs], node.id)
        return id2node
    tree = getTree(linkage_matrix)
    result = {}
    for _id in tree:
        item = tree[_id]
        result[_id] = {
            # 'id': item.id,
            'child_num': item.child_num,
            'parent': None if(item.parent is None) else item.parent.id,
            'childs': [child.id for child in item.childs],
        }
    writeJson(tree_path, result)

# 找到最相近的重要诗词并且分类
def getSimCat():
    index = 4

    # tree = loadJson(tree_path)
    imp_ids = getImpIds(imp_ids_num) #[node_id for node_id in tree if len(tree[node_id]['childs'])==0]

    imp_id1 = imp_ids[0]
    imp_ids_set = set(imp_ids)

    ids = getAllIds()[index*180000:(index+1)*180000]
    ids2sim_imp = {}
    count = 0
    print('开始循环', len(ids), len(imp_ids))
    for _id in ids:
        if _id in imp_ids_set:
            ids2sim_imp[_id] = _id
        else:
            max_sim_id = imp_id1
            def getSim(t_id):
                if _id not in docvecs or t_id not in docvecs:
                    return -999
                # print(_id, t_id, docvecs.similarity(_id, t_id), '存在')
                return docvecs.similarity(_id, t_id)
            max_sim = getSim(max_sim_id)
            for imp_id in imp_ids:
                sim = getSim(imp_id)
                if sim>max_sim:
                    # print(max_sim_id, max_sim, imp_id, sim)
                    max_sim = sim 
                    max_sim_id = imp_id
            ids2sim_imp[_id] = max_sim_id
            # print(max_sim_id, _id, imp_id1)
            count += 1
            if count%1000==0:
                print(count, len(ids), index)
                # break
    writeJson(str(index) +'.json', ids2sim_imp)

getSimCat()
# getImpCat()