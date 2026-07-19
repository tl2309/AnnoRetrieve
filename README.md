# AnnoIndex: Structure-then-Query for Precise Analytical Queries over Unstructured Documents

**AnnoIndex** enables precise analytical SQL‑like queries over unstructured text documents by automatically inducing structured schemas, building a materialised annotation index, and executing queries with progressive extraction and attribute reuse.

---

## 📁 Project Structure

```
annolindex/
├── config.py                 # Global configuration (paths, thresholds, LLM settings)
├── data_loader.py            # Load raw documents, ground truth CSVs, and query files
├── utils.py                  # Normalisation utilities (dates, numbers, strings)
├── llm.py                    # OpenAI API wrapper (with retry logic)
├── cal_sel.py                # Selectivity calculation (from QUEST, reused)
├── util_order.py             # SQL parsing, filter ordering, Boolean evaluation
├── schema_induction.py       # SchemaLoop: three‑layer schema induction with verification
├── annotation_index.py       # Structured annotation index with virtual fields & promotion
├── query_engine.py           # Query parser, executor, and EXTRACT operator
├── evaluator.py              # Precision/Recall/F1 calculation against ground truth
├── main.py                   # End‑to‑end experiment runner
└── README.md                 # This file
```

---

## ⚙️ Installation

### Prerequisites
- Python 3.9+
- OpenAI API key (for GPT‑4o)

### Steps
```bash
# Clone the repository
git clone https://github.com/your-org/annolindex.git
cd annolindex

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**requirements.txt**:
```
openai==0.28.0
pandas==1.5.3
numpy==1.24.3
torch==2.0.1
transformers==4.31.0
cupy==13.0.0
nltk==3.8.1
```

---

## 📂 Data Preparation

Place your document collections in the following directory structure:

```
data/
├── raw/
│   ├── lcr/                 # Legal case reports (each file a .txt)
│   │   ├── case001.txt
│   │   ├── case002.txt
│   │   └── ...
│   ├── wikitext/            # Wikipedia‑style articles (players, teams, etc.)
│   │   ├── player001.txt
│   │   └── ...
│   └── swde/                # Web pages (universities, movies, etc.)
│       ├── page001.txt
│       └── ...
├── ground_truth/            # (Optional) CSV files with per‑document attribute values
│   ├── lcr.csv
│   ├── wikitext.csv
│   └── swde.csv
└── queries/                 # SQL query files (one query per line)
    ├── lcr.txt
    ├── wikitext.txt
    └── swde.txt
```

### Ground Truth CSV Format
Each CSV must contain a column `doc_id` matching the document filenames (without `.txt`), followed by attribute columns. Example (`lcr.csv`):

| doc_id   | court_name     | hearing_year | judgment_year | verdict   |
|----------|----------------|--------------|---------------|-----------|
| case001  | Federal Court  | 2006         | 2007          | dismissed |
| case002  | Supreme Court  | 2009         | 2009          | upheld    |

If ground truth is not provided, the system will still run but skip evaluation.

### Query Files
Each `.txt` file contains one SQL query per line. Comments (lines starting with `...` or `--`) are ignored.  
The queries must reference the dataset name (e.g., `FROM LCR`, `FROM WikiText`, `FROM SWDE`) as shown in the sample files provided.

---

## 🔧 Configuration

Edit `config.py` to set:

- **Paths**: `DATA_ROOT`, `INDEX_DIR`, `RESULT_DIR`
- **OpenAI Key**: `OPENAI_KEY` (or set environment variable `OPENAI_KEY`)
- **SchemaLoop thresholds**: `SR_THRESHOLD` (0.6), `FE_THRESHOLD` (0.3)
- **Query engine**: `LLM_BUDGET`, `REUSE_THRESHOLD`, `EXTRACT_ORDER`

**Example**:
```python
OPENAI_KEY = "sk-..."
```

---

## 🚀 Running the System

Run the main script:

```bash
python main.py
```

This will:
1. Load documents, ground truth (if any), and queries for each dataset (`lcr`, `wikitext`, `swde`).
2. Perform **SchemaLoop** to induce three‑layer schemas.
3. Build the **structured annotation index** (materialised attribute store).
4. For each query:
   - Parse the SQL `WHERE` clause.
   - Apply **schema‑bound filtering** on the index.
   - Execute **progressive EXTRACT** on the remaining documents (using regex → SLM → LLM).
   - Persist extracted values as **virtual fields** for reuse.
5. Compute **Precision, Recall, F1** against ground truth and report **total LLM calls**.
6. Save results (the retrieved documents with attributes) to `results/`.

---

## 📊 Output

- **Console log**: Per‑query results, dataset‑level metrics, and overall summary.
- **`results/{dataset}_output.csv`**: Retrieved documents with all extracted attributes.
- **`results/{dataset}_metrics.json`**: Precision, Recall, F1, and LLM call count.

---

## 🧪 Customising the System

### Adding a New Dataset
1. Place raw `.txt` files in `data/raw/my_dataset/`.
2. (Optional) Provide ground truth as `data/ground_truth/my_dataset.csv`.
3. Create `data/queries/my_dataset.txt` with your SQL queries (use `FROM my_dataset`).
4. The system will automatically detect and process it.

### Adjusting Extraction Models
Modify the `_extract_attribute` method in `query_engine.py`:
- **Regex**: For simple patterns (fast, zero cost).
- **SLM**: Use a smaller model (e.g., `distilbert`) for moderate complexity.
- **LLM**: Use GPT‑4o for deep semantic reasoning (expensive).

### Changing the Reuse Policy
- `REUSE_THRESHOLD` (in `config.py`) controls how many extractions are needed before promoting a virtual field to a permanent schema attribute.

---

## 📈 Evaluation & Reproducibility

We reused the exact query sets from the QUEST system (provided in `data/queries/*.txt`) to ensure fair comparison.  
To reproduce the paper’s results:
- Run `main.py` – the system will output F1 scores and LLM token consumption (approximated by call count).

---

## 🤝 Contributing

We welcome contributions! Please open an issue or pull request for:
- New extraction backends (e.g., open‑source LLMs).
- Additional optimisation strategies.
- Support for multi‑table joins.

---

## 📄 License

This project is released under the MIT License.

---

## 📖 Citation

If you use this code in your research, please cite the original paper:

```
@inproceedings{annolindex2027,
  author    = {Anonymous Author(s)},
  title     = {Structure-then-Query: Enabling Precise Analytical Queries over Unstructured Documents},
  booktitle = {Proceedings of SIGMOD 2027},
  year      = {2027},
}
```

---

## 💬 Contact

For questions or issues, please open a GitHub issue or contact the authors via the paper’s anonymous submission system.

---

*Happy querying!*
