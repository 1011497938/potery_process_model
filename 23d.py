# 分层画星星
from sklearn.manifold import TSNE
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from commonFunction import writeJson, loadJson
import json
import os
from getPotery import getAllIds, getImpIds, getPoteryVec128d
import numpy as np

# imp_ids = getImpIds()
# print(imp_ids[10])
imp_ids_num = 10000
tree_path = './data/potery_tree_10000.json' 
cat_path = './data/poteryCat10000/10000.json' 

class TreeNode(object):
    def __init__(self, _id):
        self.id = _id
        self.parent = None
        self.childs = set()
        self.child_num = None
        self.vec3d = None
        self.vec128d = None

    def getChildIds(self):
        return [child.id for child in self.childs]

    def getChilds(self):
        all_childs = list(self.childs)
        # print(self.id, [child.id for child in self.childs])
        for child in self.childs:
            all_childs += child.getChilds()
        return all_childs

    def get6GrandParent(self):
        point = self
        for time in range(12):
            if point.parent is not None:
                point = point.parent
            else:
                return None
        # print(self.id , point.id)
        return point

    # def getChildInDepth(self, depth):
    #     all_childs = list(self.childs)
    #     if(depth==1):
    #         return all_childs
    #     for child in self.childs:
    #         all_childs += child.getChildInDepth(depth-1)
    #     return all_childs

    def getLeaves(self):
        all_childs = self.getChilds()
        # if len(all_childs)==0:
        #     return [self] 
        return [node for node in all_childs if len(node.childs)==0]

    def getImpPoteries(self):
        all_childs = self.getLeaves()
        # all_childs = self.getChilds()
        # all_childs = [node for node in all_childs if len(node.childs)==0]
        return [imp_ids[int(node.id)] for node in all_childs]

    def getAllPoteries(self):
        if len(self.childs)==0:
            imp_id = imp_ids[int(self.id)]
            return cat2poteries[imp_id]
        imp_poteries = self.getImpPoteries()
        all_poteries = []
        for p in imp_poteries:
            all_poteries += cat2poteries[p]
        return all_poteries

class NodeCompany():
    def __init__(self):
        self.id2node = {}

    def get(self, _id):
        if _id is None:
            return None
        _id = str(_id)
        id2node = self.id2node
        if _id not in id2node:
            id2node[_id] = TreeNode(_id)
        return id2node[_id] 

    def load(self):
        tree_json = loadJson(tree_path)
        for _id in tree_json:
            node_data = tree_json[_id]
            node = self.get(_id)
            node.parent = self.get(node_data['parent'])
            node.childs = [self.get(child_id) for child_id in node_data['childs']]
            node.child_num = node_data['child_num']

            if node.parent is None:
                self.root_node = node

    def getNodeAtLevel(self, level):
        nodes = [self.root_node]
        for index in range(level):
            children = []
            for node in nodes:
                children += node.childs
            nodes = children
        return nodes


imp_ids = getImpIds(imp_ids_num)
cat2poteries = loadJson(cat_path)

nodeCompany = NodeCompany()
nodeCompany.load()

# test = nodeCompany.get(831)
# print(test.id)
# print(test.parent.id)
# print(test.vec3d, test.getChildIds())

# print(len(nodeCompany.root_node.getAllPoteries()), len(getAllIds()))

def getCenterVec(vecs):
    vecs = np.array(vecs)
    # size = len(vecs[0].tolist())
    # center_vec = np.zeros(size)
    # for vec in vecs:
    #     center_vec += vec
    # center_vec /= len(vecs)
    return vecs.mean(0)


# 精简成几层
simpNodeCompany = NodeCompany()
simp_node_ids = set([nodeCompany.root_node.id])
simpNodeCompany.root_node= simpNodeCompany.get(nodeCompany.root_node.id)
def neighborNotInSimp(node):
    if node.parent is not None and node.parent.id in simp_node_ids:
        return False
    for child in node.childs:
        if child.id in simp_node_ids:
            return False
    return True

for index, imp_id in enumerate(imp_ids):
    node = nodeCompany.get(index)
    simp_node_ids.add(str(index))
    while node is not None:
        if neighborNotInSimp(node):
            simp_node_ids.add(node.id)
            node = node.get6GrandParent()
        else:
            break

# print(len(simp_node_ids), '831' in simp_node_ids)
for node_id in simp_node_ids:
    node = nodeCompany.get(node_id)
    sim_node = simpNodeCompany.get(node_id)
    sim_node.child_num = node.child_num
    parent = node.parent
    while parent is not None:
        # print(node.id, parent.id)
        if parent.id in simp_node_ids:
            parent = simpNodeCompany.get(parent.id)
            parent.childs.add(sim_node)
            sim_node.parent = parent
            break
        parent = parent.parent
    if sim_node.parent is None and sim_node!=simpNodeCompany.root_node:
        sim_node.parent = simpNodeCompany.root_node
        simpNodeCompany.root_node.childs.append(sim_node)

nodeCompany = simpNodeCompany
all_nodes = [nodeCompany.id2node[key] for key in nodeCompany.id2node]
for node in all_nodes:
    if node.parent is None:
        print('警告没有parent', node.id, node.getChildIds())
    if len(node.childs)==0 and int(node.id)>imp_ids_num:
        print('警告没有child', node, node.getChildIds(), node.parent.id)

for node in all_nodes:
    poteries = node.getAllPoteries()
    vecs = [getPoteryVec128d(potery) for potery in poteries]
    node.vec128d = getCenterVec(vecs)

tsne3d=TSNE(n_components=3, n_iter=1000, learning_rate=250, perplexity=10)
# tsne128d=TSNE(n_components=128, n_iter=250, learning_rate=500, perplexity=10)
nodeCompany.root_node.vec128d = np.zeros(128)
nodeCompany.root_node.vec3d = np.zeros(3)
# print([node.id for node in all_nodes if int(node.id)>2999])
# print([node_id for node_id in simp_node_ids if int(node_id)>2999])

for node in all_nodes:
    if node.id=='831':
        print('188', node.id)
    childs = node.childs
    if len(childs)==0:
        continue
    vecs = [child.vec128d-node.vec128d for child in childs]
    vecs = tsne3d.fit_transform(vecs)
    # center_vec = getCenterVec(vecs)
    for index, child in enumerate(childs):
        child.vec3d = vecs[index]
        if node.id=='831':
            print(child.vec3d, child.id, node.id)


# for node in all_nodes:
#     if len(node.childs) != 0:
#         print(node.id, [child.id for child in node.childs], node.parent.id)
# print(len(all_nodes), [node.id for node in all_nodes])
# for node in all_nodes:
#     if node.vec3d is None:
#         print( node.id, node.parent.id, [child.id for child in node.parent.childs])

for node in all_nodes:
    childs = node.getChilds()
    for child in childs:
        # print(node.id, child.id, node.parent.id,node.vec3d, child.vec3d)
        child.vec3d += node.vec3d

# def getVecSize(vec):
#     return len(vec.tolist())

# 生成每个小星系
potery2vec_path = './data/poteryCat10000/potery2vec3d.json'
potery2vec = loadJson(potery2vec_path)
# for imp_id in imp_ids:
#     poteries = cat2poteries[imp_id]
#     vecs = [getPoteryVec128d(potery) for potery in poteries]
#     vecs = tsne3d.fit_transform(vecs)
#     for index, vec in enumerate(vecs):
#         potery2vec[poteries[index]] = vec.tolist()
# writeJson(potery2vec_path, potery2vec)

# test = nodeCompany.get(831)
# print(test.id)
# print(test.parent.id)
# print(test.vec3d, test.getChildIds())

# print(imp_ids)
for index, imp_id in enumerate(imp_ids):
    poteries = cat2poteries[imp_id]
    node = nodeCompany.get(index)
    for p_id in poteries:
        vec = potery2vec[p_id]
        vec = np.array(vec)
        # 这里有个bug, 88592 [-26.0718441    7.09674025   5.34221125] None 53171 831
        try:
            vec += node.vec3d
        except :
            print(p_id,vec, node.vec3d, imp_id, index)
        
        potery2vec[p_id] = vec.tolist()
writeJson('vec.json', potery2vec)
