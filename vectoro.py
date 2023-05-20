import random
import string
import threading
from datetime import datetime, timedelta
import numpy as np
from enum import Enum
import tensorflow as tf
import tensorflow_hub as hub
import time
import os
import psutil
import json

class SimilarityAlgorithm(Enum):
    COSINE = "cosine"

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)
    
class SearchThread(threading.Thread):
    def __init__(self, vectors, query: str, similarity_algorithm):
        super().__init__()
        self.vectors = vectors
        self.query = query
        self.vector = self.model([self.query]).numpy()[0]
        self.similarity_algorithm = similarity_algorithm
        self.results = []

    def reduce_similarity_for_older_content(date_string: str, similarity: float) -> float:
        today = datetime.today().date()
        input_date = datetime.strptime(date_string, "%Y-%m-%d").date()
        days_difference = (today - input_date).days

        # anything over 100 days is considered too old
        if days_difference >= 100:
            return 0

        new_similarity = similarity * (1 - 0.01 * days_difference)
        return new_similarity
    
    def is_date_within_days(date_str, days):
        try:
            input_date = datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            print(f"Invalid date format: {date_str}")
            return False

        today = datetime.now()
        delta = timedelta(days=days)

        if today - delta <= input_date <= today:
            return True
        return False

    def run(self):
        for vector in self.vectors:
            if self.query is None or self.query.strip() == "":
                if self.is_date_within_days(vector["date"], 1):
                    self.results.append({"text": vector["text"], "similarity": similarity, "date": vector["date"]})
            elif self.similarity_algorithm == SimilarityAlgorithm.COSINE:
                similarity = np.dot(self.vector, vector["vector"]) / (np.linalg.norm(self.vector) * np.linalg.norm(vector["vector"]))
                similarity = SearchThread.reduce_similarity_for_older_content(vector["date"], similarity)
                self.results.append({"text": vector["text"], "similarity": similarity, "date": vector["date"]})

class vectoro:
    def __init__(self, similarity_algorithm=SimilarityAlgorithm.COSINE, num_threads=20, json_file='vector_data.json'):
        self.vectors = []
        self.similarity_algorithm = similarity_algorithm
        self.num_threads = num_threads
        self.json_file = json_file
        print("Loading Google Universal Sentence Encoder v5...", end="", flush=True)
        self.model = hub.load("https://tfhub.dev/google/universal-sentence-encoder-large/5")
        print("end",end="\n")

        if os.path.exists(json_file):
            self.load_from_json(json_file)

    def add_vector(self, vector, text, date):
        self.vectors.append({"vector": vector, "text": text, "date": date})

    def search(self, query: str, top_k=5):
        vectors_per_thread = len(self.vectors) // self.num_threads
        threads = []

        for i in range(self.num_threads):
            start = i * vectors_per_thread
            end = (i + 1) * vectors_per_thread if i < self.num_threads - 1 else len(self.vectors)
            thread = SearchThread(self.vectors[start:end], query, self.similarity_algorithm)
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        results = []
        for thread in threads:
            results.extend(thread.results)

        results.sort(key=lambda x: x["similarity"], reverse=True)

        return results[:top_k]

    def save_to_json(self, filename=None):
        if filename is None:
            filename = self.json_file

        with open(filename, 'w') as f:
            json.dump(self.vectors, f, cls=NumpyEncoder)

    def load_from_json(self, filename=None):
        if filename is None:
            filename = self.json_file

        with open(filename, 'r') as f:
            self.vectors = json.load(f)

        # Convert vectors back to numpy arrays
        for vector_data in self.vectors:
            vector_data["vector"] = np.array(vector_data["vector"])

def random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def get_memory_usage():
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    return mem_info.rss / (1024 * 1024 * 1024)  # Return memory usage in GB

if __name__ == "__main__":

    sfvs = vectoro()
    print("Loading Google Universal Sentence Encoder v5...", end="", flush=True)
    model = hub.load("https://tfhub.dev/google/universal-sentence-encoder-large/5")
    print("end",end="\n")

    """
    num_vectors = 1000
    target_index = random.randint(0, num_vectors - 1)

    start = time.time()
    for i in range(num_vectors):
        text = "Twitter is an American microblogging and social networking service." if i == target_index else random_string(500)
        vector = model([text]).numpy()[0]
        if i % 100 == 0:
            end = time.time()
            print(f"Inserted {i} entries in {end - start:.2f} seconds")
        sfvs.add_vector(vector, text)
    end = time.time()
    print(f"upsert Elapsed time: {end - start:.2f} seconds")

    print(f"Memory usage : {get_memory_usage():.2f} GB")
    """

    start = time.time()
    query = "What's the future of gold?"
    query_vector = model([query]).numpy()[0]
    results = sfvs.search(query_vector)
    end = time.time()
    print(f"query Elapsed time: {end - start:.2f} seconds")

    for result in results:
        print(f"Text: {result['text']}\nSimilarity: {result['similarity']}\n")
