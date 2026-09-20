import time
import numpy as np

np.random.seed(42)

q_emb = np.random.rand(768).tolist()
c_emb_list = [np.random.rand(768).tolist() for _ in range(1000)]

def old_method():
    semantic_scores = {}
    for i, c_emb in enumerate(c_emb_list):
        if sum(abs(v) for v in c_emb) > 1e-5 and sum(abs(v) for v in q_emb) > 1e-5:
            semantic_scores[i] = 1.0
    return semantic_scores

def new_method():
    semantic_scores = {}
    q_emb_valid = np.sum(np.abs(q_emb)) > 1e-5
    if q_emb_valid:
        for i, c_emb in enumerate(c_emb_list):
            if np.sum(np.abs(c_emb)) > 1e-5:
                semantic_scores[i] = 1.0
    return semantic_scores

start = time.time()
for _ in range(100):
    old_method()
old_time = time.time() - start

start = time.time()
for _ in range(100):
    new_method()
new_time = time.time() - start

print(f"Old time: {old_time:.4f}s")
print(f"New time: {new_time:.4f}s")
print(f"Improvement: {old_time / new_time:.2f}x")
