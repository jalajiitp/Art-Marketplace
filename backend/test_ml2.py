import ml
import numpy as np

class MockUser:
    def __init__(self, _id):
        self.id = _id
        self.artworks = []
        self.acquired_artworks = []
        self.liked_artworks = []

class MockArt:
    def __init__(self, _id, emb=None, created_at=None):
        self.id = _id
        self.embedding = emb
        self.created_at = created_at
        self.liked_by = []
    def __repr__(self):
        return f"Art(id={self.id})"

u = MockUser(1)
a1 = MockArt(1, [0.0, 0.0])
a2 = MockArt(2, [1.0, 1.0])
u.artworks = [a1]

print("Case 4 (avg_embedding norm is zero, art_vec norm is not zero):")
print(ml.get_hybrid_recommendations(u, [a2]))
