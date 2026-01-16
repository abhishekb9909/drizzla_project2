# Document RAG Pipeline

A robust Retrieval-Augmented Generation (RAG) pipeline for document processing, vectorization, and interactive querying. This project utilizes Azure OpenAI for intelligent document interaction.

## Prerequisites
- **Python**: Version 3.9 or higher (Python 3.11 recommended)
- **Git**: Installed and available in the system PATH
- **LibreOffice**: Must be installed to enable `.doc` → `.docx` conversion
- **Rust**: Optional, required only if building FAISS from source

## Installation

### 1. Clone the Repository

This project relies on submodules. It is **critical** to clone the repository recursively to ensure all dependencies are downloaded.

```bat
git clone --recursive https://github.com/abhishekb9909/drizzla_project2
cd drizzla_project2
```

*If you have already cloned the repository without the recursive flag, you can initialize the submodules manually:*
```bat
git submodule update --init --recursive
```

### 2. Setup

If you prefer to set up the environment manually:

1.  **Create Virtual Environment:**
    ```bat
    python -m venv venv
    ```

2.  **Activate Virtual Environment:**
    ```bat
    venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    ```bat
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    or 
    py -3.11 -m pip install -r requirements.txt

    ```

4.  **Configuration:**
    Copy the example environment file:
    ```bat
    copy .env.example .env
    ```

## Environment Configuration

Open the newly created `.env` file in your text editor and populate it with your Azure OpenAI credentials and other required settings.

## System Configuration

**LibreOffice Path**: Update the LIBREOFFICE_PATH variable in document-rag-pipeline/ingestion/doc_converter.py to match the LibreOffice installation path on your system

## Usage

The pipeline operates in two distinct phases. Ensure your virtual environment is activated before running these commands.

### Phase 1: Ingestion & Vectorization (Done by Roschelle)
Navigate to the pipeline directory to process documents and build vectors.

#### 1. Ingest a Document
Run the ingestion script and provide a file path when prompted. You can use the included sample files:

```bat
cd document-rag-pipeline

python main.py
or
py -3.11 main.py
```
**Sample Inputs (copy and paste when prompted):**
- **PDF**: `data\raw_docs\AI CONCLAVE REPORT.pdf`
- **Word (Modern)**: `data\raw_docs\Task.docx`
- **Word (Legacy)**: `data\raw_docs\Task.doc`
- **Excel**: `data\raw_docs\Test.xlsx`

#### 2. Create Vectors
Once a document is ingested (and `chunks.json` is created), generate its vectors:
```bat
python vectorize.py
or
py -3.11 vectorize.py
```

### Phase 2: RAG Pipeline & Application Running (Done by Abhishek)
Return to the root directory to run the interactive application or API server.

```bat
cd ..

python src/main_app.py
or
py -3.11 src/main_app.py

python src/api_server.py
```

### Debugging tools
Tools for debugging the pipeline are available in the source directory.

```bat
python src/debug_tools.py
```

## Troubleshooting


- **Submodules empty**: If the `document-rag-pipeline` folder is empty, run `git submodule update --init --recursive`.
