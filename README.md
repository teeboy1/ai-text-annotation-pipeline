# Customer Support Intent Annotation & Data Quality Pipeline

A portfolio project demonstrating an end-to-end AI training data workflow using a public customer-support dataset.

## Objective

Build a small, auditable dataset-quality pipeline that:

1. ingests public customer-support training data;
2. creates a representative 300-record working sample;
3. profiles and validates the source data;
4. applies an annotation/review schema;
5. identifies ambiguous and low-confidence examples;
6. measures annotation quality with Python and SQL;
7. produces reproducible QA reports.

## Source dataset

Bitext Customer Service Tagged Training Dataset for LLM-based Virtual Assistants.

The source dataset contains customer-service instructions, categories, intents, responses and language-generation tags. See the original repository and dataset documentation:

- https://github.com/bitext/customer-support-llm-chatbot-training-dataset
- https://huggingface.co/datasets/bitext/Bitext-customer-support-llm-chatbot-training-dataset

This repository does not claim ownership of the source data. Check the source license before redistributing data.

## Project status

- [x] Project scope
- [x] Repository structure
- [x] Sampling script
- [x] Annotation schema
- [x] Annotation guidelines
- [x] QA validation script
- [x] SQL analysis starter
- [ ] Run against source dataset
- [ ] Complete reviewed annotations
- [ ] Final QA report
- [ ] Portfolio screenshots
- [ ] Vercel project page

## Reproducibility

Install dependencies:

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
pip install -r requirements.txt
```

Then run:

```bash
python src/download_and_sample.py
python src/validate_annotations.py
```

The sampling script uses the Hugging Face `datasets` package and creates a 300-row stratified sample across the available intents.

## Important

The source dataset already contains labels. The portfolio contribution is the **independent data-quality/review layer**, not a claim that the source labels were created by this project.
