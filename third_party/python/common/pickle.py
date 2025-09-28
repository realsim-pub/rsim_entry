import base64
import _pickle as cPickle

def serialize(content):
    data = cPickle.dumps(content)
    return base64.encodebytes(data).decode('utf-8')

def deserialize(content):
    params = bytes(content, 'utf-8')
    res = base64.b64decode(params)
    de_serialize_content = cPickle.loads(res)
    return de_serialize_content
    