import json

def writeJson(path, json_object):
    f = open('./data/'+path+'.json', 'w', encoding='utf-8')
    f.write(json.dumps(json_object, ensure_ascii=False, sort_keys=True, indent=1))  #
    f.close()
    return

def loadJson(path):
    f = open(path, 'r', encoding='utf-8')
    _object = json.loads(f.read())
    f.close()
    return _object

# 写一个部分排序
# def 