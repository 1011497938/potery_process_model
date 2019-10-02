from sklearn.cluster import KMeans
# 分层画星星
from sklearn.manifold import TSNE
from commonFunction import writeJson, loadJson
import json
import os
from getPotery import getAllIds, getImpIds, getPoteryVec128d
import numpy as np

cat_tree_path = './data/catTree.json'
count = 0
def getCatTree():
    id2node = {}
    max_levae_num = 60
    class TreeNode(object):
        def __init__(self, potery_ids, parent):
            global count
            self.id = str(count)
            count+=1
            self.parent = parent
            self.childs = []
            self.potery_ids = potery_ids
            self.loadChilds()

            id2node[self.id] = self
            if not self.isLeave():
                self.potery_ids = []

        def getParentId(self):
            if self.parent is not None:
                return self.parent.id
            else:
                return None

        def isLeave(self):
            return len(self.potery_ids)<max_levae_num

        def loadChilds(self):
            potery_ids = self.potery_ids
            if self.isLeave():
                return

            vecs = [getPoteryVec128d(_id) for _id in potery_ids]
            labels = KMeans(n_clusters=max_levae_num-2, max_iter=2000, n_jobs=-1).fit_predict(vecs)

            label2id = {}
            for index, label in enumerate(labels):
                label = str(label)
                if label not in label2id:
                    label2id[label] = []
                label2id[label].append(potery_ids[index])
            self.childs = [TreeNode(label2id[label], self) for label in label2id if len(label2id[label])>0]

    ids = getAllIds()
    TreeNode(ids, None)

    id2dict = {}
    # temp_ids = []
    for _id in id2node:
        node = id2node[_id]
        new_dict = {
            'childs': [child.id for child in node.childs],
            'parent': node.getParentId(),
            'potery_ids': node.potery_ids if(node.isLeave()) else []
        }
        # temp_ids += node.potery_ids
        id2dict[_id] = new_dict
    # temp_ids = set(temp_ids)
    # print('保存了', len(temp_ids))
    writeJson(cat_tree_path, id2dict)

def getVecs():
    class NodeCompany():
        def __init__(self):
            self.id2node = {}
            self.root_node = None

        def getAllNodes(self):
            return [self.id2node[key] for key in self.id2node]

        def get(self, _id):
            if _id is None:
                return None
            _id = str(_id)
            id2node = self.id2node
            if _id not in id2node:
                id2node[_id] = TreeNode(_id)
            return id2node[_id] 

        def load(self):
            tree_json = loadJson(cat_tree_path)
            for _id in tree_json:
                node_data = tree_json[_id]
                node = self.get(_id)
                node.parent = self.get(node_data['parent'])
                node.childs = [self.get(n_id) for n_id in node_data['childs']]
                # if node.parent is not None:
                #     node.parent.childs.append(node)
                node.potery_ids =  node_data['potery_ids']
                node.is_leave = len(node.potery_ids) > 0
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

    class TreeNode:
        def __init__(self, _id):
            self.id = _id
            self.parent = None
            self.childs = []
            self.potery_ids = []
            self.is_leave = False
            self.vec3d = None
            self.vec128d = None
            self.level = 1

        def getAllChilds(self):
            all_childs = list(self.childs)
            for child in self.childs:
                all_childs += child.getAllChilds()
            return all_childs

        def getLeaves(self):
            all_childs = self.getAllChilds()
            return [node for node in all_childs if len(node.childs)==0]

        def getParentId(self):
            if self.parent is not None:
                return self.parent.id
            else:
                return None

        def getAllPoteries(self):
            if self.is_leave:
                # print(self.id)
                return self.potery_ids
            leaves = self.getLeaves()
            # if len(leaves)==0:
            #     print(self.id)
            poteries = []
            for leaf in leaves:
                poteries += leaf.potery_ids
            # if len(poteries)>0:
            #     print(len(poteries))
            return poteries

    nodeManager = NodeCompany()
    nodeManager.load()
    root_node = nodeManager.root_node

    def getCenterVec(vecs):
        vecs = np.array(vecs)
        return vecs.mean(0)

    print(root_node, root_node.id, len(root_node.getAllPoteries()),len(root_node.getAllChilds()))
    print('第一步')
    # print([node.id  for node in root_node.getAllChilds()])
    all_nodes = nodeManager.getAllNodes()
    for node in all_nodes:
        point = node
        while point.parent is not None:
            node.level += 1
            point = point.parent

    print('第二步')
    for node in all_nodes:
        poteries = node.getAllPoteries()
        vecs = [getPoteryVec128d(p_id) for p_id in poteries]
        # print(poteries,)
        node.vec128d = getCenterVec(vecs)

    tsne3d=TSNE(n_components=3, n_iter=300, learning_rate=250, perplexity=10)
    root_node.vec128d = np.zeros(128)
    root_node.vec3d = np.zeros(3)
    print('第三步')
    for node in all_nodes:
        childs = node.childs
        if len(childs)==0:
            continue
        if len(childs)==1:
            childs[0].vec3d = np.zeros(3)
            continue
        vecs = [child.vec128d for child in childs]
        vecs = tsne3d.fit_transform(vecs)
        center_vec = getCenterVec(vecs)

        size = pow(len(node.getAllPoteries())+1, 1/3) 
        for index, child in enumerate(childs):
            child.vec3d = (vecs[index] - center_vec) * size

    print('第四步')
    for node in all_nodes:
        childs = node.getAllChilds()
        for child in childs:
            child.vec3d += node.vec3d

    pid2vec = {}
    leaves = root_node.getLeaves()
    for leaf in leaves:
        potery_ids = leaf.potery_ids
        if len(potery_ids)==1:
            p_id = potery_ids[0]
            pid2vec[p_id] = np.zeros(3)
            continue
        
        vecs = [getPoteryVec128d(p_id) for p_id in potery_ids]
        vecs = tsne3d.fit_transform(vecs)
        center_vec = getCenterVec(vecs)
        for index, p_id in enumerate(potery_ids):
            pid2vec[p_id] = vecs[index] - center_vec + leaf.vec3d

    print('第五步')
    for p_id in pid2vec:
        pid2vec[p_id] = pid2vec[p_id].tolist()

    writeJson('vec.json', pid2vec)

getCatTree()
getVecs()