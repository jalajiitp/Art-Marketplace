import os
import numpy as np
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Setup Gemini API key
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def generate_embedding(text: str) -> list[float]:
    """Generates an embedding vector for the given text using Gemini."""
    if not api_key:
        # Fallback to random embedding for dev if no API key
        vec = np.random.rand(768)
        vec = vec / np.linalg.norm(vec)
        return vec.tolist()
        
    try:
        # Using embedding-001 model as per user requirements
        result = genai.embed_content(
            model="models/gemini-embedding-2",
            content=text,
            task_type="retrieval_document"
        )
        return result['embedding']
    except Exception as e:
        print(f"Warning: Failed to generate embedding ({e}). Fallback to random.")
        vec = np.random.rand(768)
        vec = vec / np.linalg.norm(vec)
        return vec.tolist()

def get_similar_artworks(target_embedding: list[float], all_artworks: list, n_results: int = 5):
    """
    Computes cosine similarity between target_embedding and all_artworks manually using NumPy.
    Returns the top n_results similar artworks (excluding itself).
    """
    if not target_embedding or not all_artworks:
        return []
        
    target_vec = np.array(target_embedding)
    target_norm = np.linalg.norm(target_vec)
    
    if target_norm == 0:
        return []
        
    similarities = []
    
    for artwork in all_artworks:
        if not artwork.embedding:
            continue
            
        artwork_vec = np.array(artwork.embedding)
        artwork_norm = np.linalg.norm(artwork_vec)
        
        if artwork_norm == 0:
            continue
            
        # Cosine similarity = dot(A, B) / (norm(A) * norm(B))
        sim = np.dot(target_vec, artwork_vec) / (target_norm * artwork_norm)
        similarities.append((sim, artwork))
        
    # Sort by descending similarity
    similarities.sort(key=lambda x: x[0], reverse=True)
    
    # Return top N artworks
    return [item[1] for item in similarities[:n_results]]

def extract_image_features(image_path: str, title: str = "", description: str = "") -> list[float]:
    """Uses Gemini Vision to describe the image, then embeds the description."""
    if not api_key:
        return generate_embedding(f"{title} {description}")
    try:
        sample_file = genai.upload_file(path=image_path, display_name=title)
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        response = model.generate_content([
            sample_file, 
            "Describe this artwork in vivid detail, focusing on colors, subject matter, style, and mood. Provide a single detailed paragraph."
        ])
        detailed_description = response.text
        # Cleanup file from Gemini servers
        genai.delete_file(sample_file.name)
        
        full_text = f"{title}. {description}. Visuals: {detailed_description}"
        return generate_embedding(full_text)
    except Exception as e:
        print(f"Warning: Gemini vision failed ({e}). Falling back to text embedding.")
        return generate_embedding(f"{title} {description}")

def get_hybrid_recommendations(target_user, all_artworks, n_results=100):
    """
    Blends Content-Based Filtering (Cosine similarity of embeddings) 
    with Collaborative Filtering (overlap of user likes).
    """
    user_artworks = target_user.artworks + target_user.acquired_artworks + target_user.liked_artworks
    exclude_ids = [a.id for a in user_artworks]
    candidate_artworks = [a for a in all_artworks if a.id not in exclude_ids]
    
    if not candidate_artworks:
        return []
        
    if not user_artworks:
        # Cold start: return newest
        candidate_artworks.sort(key=lambda x: (x.created_at is None, x.created_at), reverse=True)
        return candidate_artworks[:n_results]

    # Content Score (using average embedding of user's engaged artworks)
    embeddings = [np.array(a.embedding) for a in user_artworks if a.embedding]
    avg_embedding = np.mean(embeddings, axis=0) if embeddings else None
    
    # Collaborative base: Users who like similar things
    target_user_liked_users = set()
    for a in user_artworks:
        for u in a.liked_by:
            target_user_liked_users.add(u.id)
            
    scores = []
    for art in candidate_artworks:
        content_score = 0
        if avg_embedding is not None and art.embedding:
            art_vec = np.array(art.embedding)
            norm = np.linalg.norm(art_vec)
            avg_norm = np.linalg.norm(avg_embedding)
            if norm > 0 and avg_norm > 0:
                content_score = np.dot(avg_embedding, art_vec) / (avg_norm * norm)
                
        # Collaborative Score
        collab_score = 0
        for u in art.liked_by:
            if u.id in target_user_liked_users:
                collab_score += 1
                
        # Normalize collab score (0 to 1 ideally)
        norm_collab = min(collab_score / max(1, len(target_user_liked_users)), 1.0)
        
        # Blend (70% content, 30% collaborative)
        hybrid_score = (0.7 * content_score) + (0.3 * norm_collab)
        scores.append((hybrid_score, art))
        
    scores.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in scores[:n_results]]

