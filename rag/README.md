# RAG Service Module

This module implements a Retrieval-Augmented Generation (RAG) assistant
for the portfolio website.

Responsibilities:
- Read portfolio knowledge from a clean text file
- Generate embeddings using Gemini
- Store and retrieve embeddings via Chroma
- Answer questions strictly from portfolio content

This module does NOT:
- Handle UI
- Manage admin authentication
- Modify portfolio data
