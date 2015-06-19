__author__ = 'charoy'
import json
import sys

id = sys.argv[1]
def load_data(id):
    filename="%sarea.json" % id
    json_data=open(filename).read()
    area=json.loads(json_data)
    return area


if __name__ == "__main__":
    print load_data(id)