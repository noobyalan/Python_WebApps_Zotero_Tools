# AI-Powered Zotero PDF Summarizer

## Overview
This project automates the process of generating AI-powered summaries for academic papers stored in **Zotero**. It extracts text from PDFs using `pdfplumber`, generates summaries using **OpenAI's API**, and automatically adds them as notes to Zotero items with a specific tag.

## Features
- 📄 Extracts text from Zotero-stored PDFs.
- 🤖 Uses OpenAI's API to generate concise academic summaries.
- 📌 Automatically attaches the generated summary as a **Zotero note**.
- 🏷️ Tags summarized notes to prevent duplicate processing.
- 📂 Allows users to select a specific **Zotero collection** for processing.

## Installation
### Prerequisites
Ensure you have the following installed:
- Python 3.8+
- Git (optional, for cloning the repository)

### Clone the Repository
```bash
git clone https://github.com/yourusername/ai-zotero-summarizer.git
cd ai-zotero-summarizer
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

## Configuration
This project requires a configuration file for Zotero and OpenAI API settings.

### Create `zotero_config.yaml`
```yaml
zotero:
  user_id: "your_zotero_user_id"
  api_key: "your_zotero_api_key"
  summary_tag: "AI-Summary"  # Tag used to identify summarized notes

openai:
  api_key: "your_openai_api_key"
  model: "gpt-4"  # OpenAI model to use
  prompt: "You are an academic assistant. Summarize this paper professionally."
```
Save this file as `zotero_config.yaml` or `zotero_config_dev.yaml` in the project directory.

## Usage
Run the script to process Zotero collections:
```bash
python main.py
```
You will be prompted to choose a Zotero collection. The script will:
1. Identify items in the selected collection.
2. Check if they already contain an AI-generated summary (to avoid duplicates).
3. Extract text from the associated PDFs.
4. Generate a summary using OpenAI's API.
5. Attach the summary as a Zotero note.

## License
This project is licensed under the **GPLv3 License**. See the [LICENSE](LICENSE) file for details.

## Contributing
Pull requests are welcome! If you'd like to contribute, please fork the repository and submit a PR with your changes.

---
⚡ **Automate your academic research workflow with AI!** 🚀

