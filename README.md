# BioLitAI: Intelligent Literature Mining and Research Gap Detection Tool

An AI-powered web application for biomedical researchers to automatically search, summarize, and analyze scientific literature to identify research gaps.

## Features

- 🔍 **Literature Search**: Search PubMed for biomedical papers
- 📝 **Intelligent Summarization**: Auto-summarize papers using Mistral-7B LLM
- 🏷️ **Named Entity Recognition**: Extract diseases, genes, drugs, methods, and datasets
- 💡 **Research Gap Detection**: AI-powered analysis to suggest potential research gaps
- 💾 **SQLite Database**: Store and retrieve research findings
- 🎨 **Interactive UI**: Streamlit-based user interface

## Tech Stack

- **Backend**: Python
- **UI Framework**: Streamlit
- **NLP Models**: Hugging Face Transformers (Mistral-7B), spaCy
- **Database**: SQLite
- **API**: PubMed (free public endpoint)

## Project Structure

```
BioLitAI/
├── README.md
├── requirements.txt
├── config.py
├── src/
│   ├── __init__.py
│   ├── pubmed_api.py          # PubMed API wrapper
│   ├── llm_summarizer.py      # LLM-based summarization
│   ├── ner_extractor.py       # Named Entity Recognition
│   ├── gap_detector.py        # Research gap detection
│   └── database.py            # SQLite database operations
├── app.py                      # Streamlit main application
└── data/
    └── bioliteai.db           # SQLite database (auto-created)
```

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/sufaismail/BioLitAI.git
   cd BioLitAI
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download spaCy model**
   ```bash
   python -m spacy download en_core_sci_md
   ```

## Usage

Run the Streamlit app:
```bash
streamlit run app.py
```

Then open your browser to `http://localhost:8501`

## How It Works

1. **Search**: Enter keywords to search PubMed
2. **Analyze**: Papers are automatically summarized and analyzed
3. **Extract**: Diseases, genes, drugs, methods, datasets are extracted
4. **Detect Gaps**: AI identifies potential research gaps
5. **Store**: Results are saved to the database for future reference

## Features in Development

- [ ] Export results to PDF/CSV
- [ ] Advanced filtering and sorting
- [ ] Collaboration features
- [ ] Citation management
- [ ] Multi-language support

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License

## Author

sufaismail

## Support

For issues, questions, or suggestions, please open an issue on GitHub.
