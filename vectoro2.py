import json
import os
import jsonpickle
import hnswlib
import numpy as np
import tensorflow_hub as hub
import tensorflow_text

"""
Candidate to replace using hnswlib C++ nearest neighbor search python wrapper

hnswlib is a Python library that implements Hierarchical Navigable Small World (HNSW) graphs for approximate nearest neighbor search.
"""

class vectoro_db:
    def __init__(self, dim=512, space='cosine'):
        self.dim = dim
        self.db = hnswlib.Index(space=space, dim=dim)
        self.db.init_index(max_elements=10000, ef_construction=200, M=16)
        self.id_map = {}
        self.encoder = hub.load("https://tfhub.dev/google/universal-sentence-encoder-large/5")

    def save_to_file(self, filename='vector_db.json'):
        with open(filename, 'w') as f:
            f.write(jsonpickle.encode((self.id_map, self.db)))

    def load_from_file(self, filename='vector_db.json'):
        with open(filename, 'r') as f:
            self.id_map, self.db = jsonpickle.decode(f.read())

    def upsert(self, text, id=None):
        vector = np.array(self.encoder([text])[0])
        id = id if id is not None else str(len(self.id_map))
        self.id_map[id] = (text, vector.tolist())
        self.db.add_items(vector, [id])

    def query(self, text, similarity_type='cosine', top_n=10):
        vector = np.array(self.encoder([text])[0])
        labels, distances = self.db.knn_query(vector, k=top_n)
        return [(self.id_map[str(label)][0], distance) for label, distance in zip(labels[0], distances[0])]

    def delete(self, id):
        self.db.mark_deleted(int(id))
        del self.id_map[id]

class vectoro_db_test:
    def __init__(self):
        self.vector_db = vectoro_db()

    def test_insert_and_query_speed(self):
        import time
        import lorem
        start = time.time()
        for i in range(10000):
            self.vector_db.upsert(lorem.sentence(), str(i))
        print('Insert time:', time.time() - start, 's')
        start = time.time()
        print(self.vector_db.query('test sentence'))
        print('Query time:', time.time() - start, 's')

def main():
    test = vectoro_db_test()
    test.test_insert_and_query_speed()

if __name__ == "__main__":
    main()
