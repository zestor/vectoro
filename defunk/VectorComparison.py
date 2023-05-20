import numpy as np

class VectorComparison:
    def euclidean_similarity(self, vec1, vec2):
        return np.linalg.norm(vec1 - vec2)
    
    def cosine_similarity(self, vec1, vec2):
        dot_product = np.dot(vec1, vec2)
        norm_vec1 = np.linalg.norm(vec1)
        norm_vec2 = np.linalg.norm(vec2)
        return dot_product / (norm_vec1 * norm_vec2)
    
    def dot_product_similarity(self, vec1, vec2):
        return np.dot(vec1, vec2)