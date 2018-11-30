import json


def bjson2object(barray):
	return json.loads(barray.decode())


def object2bjson(object):
	return json.dumps(object).encode()
