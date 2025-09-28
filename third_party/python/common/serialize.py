import dill

def object_to_str(input_object):
    return dill.dumps(input_object).hex()

def str_to_object(input_str):
    return dill.loads(bytes.fromhex(input_str))