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

# Case 1: Norm is zero
u = MockUser(1)
a1 = MockArt(1, [0.0, 0.0])
a2 = MockArt(2, [0.0, 0.0])
u.artworks = [a1]

print("Case 1 (zero norm):", ml.get_hybrid_recommendations(u, [a1, a2]))

# Case 2: Candidate has no embedding
a3 = MockArt(3, None)
print("Case 2 (no embedding on candidate):", ml.get_hybrid_recommendations(u, [a1, a3]))

# Case 3: Both have no embedding
u.artworks = [MockArt(4, None)]
print("Case 3 (no embedding on user art):", ml.get_hybrid_recommendations(u, [a3, MockArt(5, None)]))
