# Art Marketplace: Comprehensive Project Overview

This document outlines everything this Art Marketplace platform does, the complete feature set, how it works step-by-step, and the technology stack used to build it.

---

## 🚀 What the Project Does (Step-by-Step User Flow)

### 1. Authentication & Onboarding
- **Register / Login:** Users can create an account using a username, email, and password. 
- **Security:** Passwords are mathematically hashed before touching the database. Once logged in, the system uses highly secure JWT (JSON Web Tokens) with a short-lived access token in memory and a long-lived, invisible `httpOnly` refresh token to keep users logged in safely.

### 2. The Personalized Discovery Feed
- **Initial State:** If a user is not logged in or has a brand-new account, the homepage shows a beautiful, glassmorphism-styled masonry grid of the newest artwork available on the platform.
- **The Hybrid Recommender System:** Once a user logs in and starts interacting (Liking or Acquiring art), the feed dynamically transforms. It uses a custom **Hybrid Algorithm** to recommend art:
  - **Content Score (30%):** The AI calculates the average "vibe" of everything the user likes/owns based on deep visual AI features, and finds visually similar art.
  - **Collaborative Score (70%):** The system checks what *other* users (who share similar tastes) have liked, and bubbles those artworks up to the top.

### 3. Deep Semantic Search
- **AI-Powered Search:** Unlike standard search bars that only look for exact word matches in a title, this search bar is backed by Google Gemini's AI embeddings. If a user searches for "depressing moody portrait", the AI understands the *concept* and searches the database for artworks that possess those deep semantic features, regardless of their title.

### 4. Artwork Interaction & Acquisition
- **Artwork Detail Page:** Clicking an artwork opens its detail page. Here, users can see the price, description, and a carousel of "Visually Similar" artworks recommended by the AI.
- **Liking:** Users can click the ❤️ button to like an artwork. This feeds directly into the Collaborative Filtering algorithm to improve recommendations across the platform.
- **Mock Checkout:** Users can click "Acquire Artwork", which opens a mock checkout flow. 
- **Ownership Transfer:** Upon successful checkout, the database physically transfers the `owner_id` of the artwork from the original artist to the buyer.

### 5. Uploading & Selling Art
- **Upload Flow:** Artists can upload their own images, set a title, description, and price. 
- **CNN / Multi-Modal Extraction (Magic under the hood):** When an image is uploaded, the backend securely sends the raw image file to **Gemini 1.5 Flash Vision**. The AI "looks" at the image, extracts its visual essence (colors, mood, subjects, style), writes a vivid description, and translates it all into a dense mathematical vector (embedding) that is saved to the database.

### 6. User Profiles
- **Profile Dashboard:** A dedicated page where users can see their own avatar and information.
- **My Collection:** Displays a grid of all artworks the user has successfully purchased/acquired.
- **My Portfolio:** Displays a grid of all original artworks the user has uploaded for sale.

---

## 🛠️ The Technology Stack

Here is exactly what was used to build the platform, end-to-end:

### Frontend (User Interface)
- **Framework:** React.js (via Vite for blazing fast builds)
- **Language:** TypeScript for strict type-checking and bug prevention.
- **Routing:** `react-router-dom` for seamless, single-page navigation without refreshing the browser.
- **Styling:** Vanilla CSS. We custom-built a modern, premium aesthetic featuring dark mode, glassmorphism (frosted glass effects), glowing neon accents, smooth micro-animations, and dynamic masonry grids.

### Backend (Server & API)
- **Framework:** FastAPI (Python) - incredibly fast, modern web framework.
- **Server:** Uvicorn (ASGI server to run FastAPI).
- **Authentication:** `passlib` with `bcrypt` for hashing passwords, and `python-jose` for generating JWT tokens.

### Database
- **Engine:** SQLite (`sql_app.db`). A lightweight file-based database perfect for local development.
- **ORM (Object-Relational Mapping):** SQLAlchemy. This allowed us to interact with the database using Python objects instead of writing raw SQL strings.
- **Data Seeding:** We wrote a custom Python script to query the **Metropolitan Museum of Art's Open Access API**, downloading public domain artwork and seeding the initial database so it wasn't empty.

### Artificial Intelligence & Machine Learning
- **SDK:** `google-generativeai` (Google Gemini Python SDK).
- **Image Feature Extraction:** `gemini-1.5-flash` model. Used as our "CNN" to deeply analyze and describe uploaded image files.
- **Semantic Embeddings:** `models/gemini-embedding-2` model. Converts text and image descriptions into 768-dimensional mathematical arrays.
- **Vector Math:** `numpy`. Used in the backend to manually calculate "Cosine Similarity" (the mathematical distance between two artwork vectors) in real-time, powering both the search and the recommendation engine without needing a complex external vector database like ChromaDB.
