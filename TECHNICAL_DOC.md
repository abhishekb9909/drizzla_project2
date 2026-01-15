# Technical Documentation

## 1. Embedding Model Selection Criteria

The project utilizes **`all-MiniLM-L6-v2`** from the `sentence-transformers` library based on the following criteria:

*   **Efficiency & Speed**: Extremely lightweight (~80MB) and optimized for CPU inference, making it ideal for local-first deployments without GPU dependency.
*   **Performance-Size Ratio**: Consistently ranks high on the MTEB (Massive Text Embedding Benchmark) for semantic search despite its small footprint.
*   **Dimensionality**: Maps text to a dense 384-dimensional vector space, ensuring lower storage costs and faster retrieval times compared to larger models (768+ dimensions).
*   **Generalization**: Trained on 1B+ sentence pairs, providing robust performance across diverse document types (technical reports, general prose) without fine-tuning.

## 2. End-to-End RAG Pipeline Flow

The system operates in two distinct phases: **Indexing** and **Inference**.

### Phase 1: Ingestion & Indexing
1.  **Document Loading**: Supports PDF (`pdfplumber`), DOCX/DOC (`python-docx`), and Excel (`pandas`). Legacy `.doc` files are automatically converted to `.docx`.
2.  **Preprocessing**: Text is cleaned to remove excessive whitespace and artifacts.
3.  **Chunking**: Text is split into overlapping chunks (e.g., 500 characters with 50 overlap) to preserve context. Metadata (Page #, Source, Section) is attached to each chunk.
4.  **Vectorization**: Chunks are passed through `all-MiniLM-L6-v2` to generate 384-d embeddings.
5.  **Storage**:
    *   **Vectors**: Stored in a local FAISS index (`IndexFlatL2`) for generic Euclidean distance search.
    *   **Metadata**: Stored in a JSON file mapped to chunk IDs for retrieval.

### Phase 2: Retrieval & Generation (RAG)
1.  **Query Processing**: User query is embedded using the same model.
2.  **Retrieval**: FAISS performs a similarity search to find the top-k (default 3-5) most relevant text chunks.
3.  **Context Assembly**: Retrieved text chunks are formatted into a single context block, preserving source attribution.
4.  **LLM Generation**: The query + context are sent to Azure OpenAI (GPT-3.5/4).
5.  **Output**: The LLM generates a grounded answer citing the provided context, which is displayed to the user along with source references.

## 3. Known Limitations and Future Improvements

*   **Context Window**: Currently uses basic fixed-size sliding window chunking.
    *   *Improvement*: Implement semantic chunking or recursive character splitting for better context preservation.
*   **Conversation History**: The system is currently single-turn (QA only).
    *   *Improvement*: Add conversation memory to support follow-up questions.
*   **Retrieval Accuracy**: Relies solely on cosine/L2 distance.
    *   *Improvement*: Add a re-ranking step (e.g., Cross-Encoder) after initial retrieval to boost precision.
*   **Scalability**: Uses a flat local file index.
    *   *Improvement*: Migrate to a managed vector database (e.g., Qdrant, Pinecone) for handling millions of documents.
