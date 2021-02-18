from elasticsearch import Elasticsearch

import sys

if __name__ == "__main__":
    doc_name = sys.argv[1]
    es = Elasticsearch(hosts='localhost', port=9200)
    print(es.indices.delete(doc_name))
