import time
import random
import string
import math
import os
import json
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
from concurrent.futures import ThreadPoolExecutor
from VectorComparison import VectorComparison
    
class vectoro_db:
    def __init__(self, num_tables=1, num_hashes=1, filename="vectoro_db.json"):
        self.num_tables = num_tables
        self.num_hashes = num_hashes
        self.tables = [{} for _ in range(self.num_tables)]
        self.hash_funcs = self.generate_hash_funcs(self.num_tables * self.num_hashes)
        self.locks = [ThreadPoolExecutor(max_workers=1) for _ in range(self.num_tables)]
        self.filename = filename
        self.load_from_file()

    def load_from_file(self):
        if os.path.isfile(self.filename):
            with open(self.filename, "r") as f:
                data = json.load(f)
                loaded_tables = data["tables"]
                # convert vectors from list to numpy array and keys to integers
                for i in range(len(loaded_tables)):
                    table = {}
                    for key, value in loaded_tables[i].items():
                        int_key = int(key)
                        table[int_key] = [(entry[0], entry[1], np.array(entry[2])) for entry in value]
                    self.tables[i] = table
        else:
            print(f"No database file found at {self.filename}. Starting with empty data.")

    def save_to_file(self):
        # convert vectors from numpy array to list
        for i in range(len(self.tables)):
            for key, value in self.tables[i].items():
                for j in range(len(value)):
                    value[j] = (value[j][0], value[j][1], np.array(value[j][2]).tolist())
        data = {"tables": self.tables}
        with open(self.filename, "w") as f:
            json.dump(data, f)

    def generate_hash_funcs(self, num_funcs):
        hash_funcs = []
        i = 0
        while len(hash_funcs) < self.num_tables:
            a = np.random.normal(size=(512,))
            b = np.random.uniform(size=(1,))
            hash_func = (a, b)
            hash_val = hash(str(hash_func))
            if hash_val not in [hash(str(h)) for h in hash_funcs]:
                hash_funcs.append(hash_func)
            i += 1
            if i >= num_funcs:
                break
        return hash_funcs

    def hash_vector(self, vector):
        return [hash(int(np.dot(hash_func[0], vector) + hash_func[1])) for hash_func in self.hash_funcs[:self.num_tables*self.num_hashes]]

    def upsert(self, vector, text, id=None):
        if id is None:
            id = hash(text)
        hashes = self.hash_vector(vector)
        for i, hash_val in enumerate(hashes[:self.num_tables]):
            table = self.tables[i]
            with self.locks[i]:
                if hash_val in table:
                    table[hash_val].append((id, text, vector))
                else:
                    table[hash_val] = [(id, text, vector)]
    
    def query(self, vector, similarity_type='cosine', similarity_score=None):

        vc = VectorComparison()
        if similarity_type == 'cosine':
            similarity_func = vc.cosine_similarity
        elif similarity_type == 'euclidean':
            similarity_func = vc.euclidean_similarity
        elif similarity_type == 'dot_product':
            similarity_func = vc.dot_product_similarity
        else:
            raise ValueError("Invalid similarity type")
        
        hashes = self.hash_vector(vector)
        results = []
        with ThreadPoolExecutor() as executor:
            for i, hash_val in enumerate(hashes[:self.num_tables]):
                table = self.tables[i]
                if hash_val in table:
                    future = executor.submit(self.query_table, table[hash_val], vector, similarity_func)
                    results.append(future)
        matches = []
        seen_texts = set()
        for result in results:
            for match in result.result():
                text = match[1]
                if text not in seen_texts:
                    seen_texts.add(text)
                    similarity = match[0]
                    if similarity_score is None or similarity >= similarity_score:
                        matches.append((text, similarity))
        return matches

    def query_table(self, candidates, vector, similarity_func):
        matches = []
        for candidate in candidates:
            similarity = similarity_func(candidate[2], vector)
            matches.append((similarity, candidate[1]))
        matches.sort(key=lambda x: x[0], reverse=True)
        return matches
    
    def delete(self, id):
        for i in range(self.num_tables):
            table = self.tables[i]
            with self.locks[i]:
                for hash_val in list(table.keys()):
                    entries = table[hash_val]
                    table[hash_val]

class vectoro_db_test:
    def test_insert_and_query_speed(self):

        num_texts = 10000 - 1
        print(f"based on {num_texts} entries suggested parameters:")
        num_tables = math.ceil(math.log2(num_texts) / math.log2(1 / 0.1))
        num_hashes = math.ceil(512 * math.log(1 / 0.9))
        print(f"num_tables: {num_tables}")
        print(f"num_hashes: {num_hashes}")
    
        hub_module = hub.load("https://tfhub.dev/google/universal-sentence-encoder-large/5")
        
        database = vectoro_db(num_tables=num_tables, num_hashes=num_hashes)
        texts = [''.join(random.choices(string.ascii_letters + string.digits, k=500)) for _ in range(num_texts)]

        start = time.time()
        print(f"starting insert of {num_texts} entries")
        for i, text in enumerate(texts):
            embedding = hub_module([text])[0].numpy()
            database.upsert(embedding, text)
            if i % 100 == 0:
                end = time.time()
                print(f"Inserted {i} entries in {end - start:.2f} seconds")
            #if i % 10000 == 0:
            #    database.save_to_file() # Save the data to file after inserting
        end = time.time()
        print(f"Inserted {num_texts} entries in {end - start:.2f} seconds")

        
        text = "Once upon a time, there was a virtual world called Twitter. It was a place where people could express their thoughts, share their lives, and connect with others. At first, it was just a small community, but as time passed, it grew and grew until it became a global phenomenon. Twitter was a place where people could share their opinions, from the mundane to the controversial. It was a place where celebrities, politicians, and ordinary people alike could speak their minds and be heard by millions. Sometimes, Twitter was a force for good, bringing people together and amplifying important messages. Other times, it was a breeding ground for hate and harassment, with trolls and bots spreading misinformation and vitriol. Despite its flaws, Twitter remained a beloved platform for many, a place where they could find community, humor, and support. And as the years went by, it continued to evolve and adapt, remaining a fixture in the ever-changing landscape of the internet."
        embedding = hub_module([text])[0].numpy()
        database.upsert(embedding, text)
        

        start = time.time()
        query_text = "What's going on with Twitter?"
        query_embedding = hub_module([query_text])[0].numpy()
        results = database.query(query_embedding, 
                                 similarity_type='cosine', 
                                 similarity_score=0.40)
        end = time.time()

        for result in results:
            print("=====================================")
            print(f"similarity = {result[1]}")
            print(f"text = {result[0]}")

        print(f"Single query = {len(results)} results in {end - start:.2f} seconds")

        database.save_to_file() # Save the data to file after inserting

        """
        start = time.time()
        database2 = vectoro_db(num_tables=num_tables, num_hashes=num_hashes)
        end = time.time()
        print(f"Loading database from file in {end - start:.2f} seconds")

        for _ in range(10):
            start = time.time()
            query_text = "What's going on with Twitter?"
            query_embedding = hub_module([query_text])[0].numpy()
            results = database2.query(query_embedding, 
                                    similarity_type='cosine', 
                                    similarity_score=0.40)
            end = time.time()

            for result in results:
                print("=====================================")
                print(f"similarity = {result[1]}")
                print(f"text = {result[0]}")

            print(f"Single query = {len(results)} results in {end - start:.2f} seconds")
    """    

if __name__ == '__main__':
    test = vectoro_db_test()
    test.test_insert_and_query_speed()
