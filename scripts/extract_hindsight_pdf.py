#!/usr/bin/env python3
"""
Extract text from Hindsight paper PDF and convert to Markdown
"""

import pdfplumber
import re

pdf_path = "docs/research/pdf/2512.12818.pdf"
output_path = "docs/research/hindsight-paper/hindsight_paper.md"

print(f"Extracting text from {pdf_path}...")

# Extract text from PDF
full_text = ""
with pdfplumber.open(pdf_path) as pdf:
    print(f"Total pages: {len(pdf.pages)}")

    for i, page in enumerate(pdf.pages):
        print(f"Processing page {i+1}/{len(pdf.pages)}", end="\r")
        text = page.extract_text()
        if text:
            full_text += text + "\n\n"

print("\nFormatting as markdown...")

# Basic markdown formatting
# Add title from first lines
lines = full_text.split('\n')
markdown = "# Hindsight is 20/20: Building Agent Memory that Retains, Recalls, and Reflects\n\n"
markdown += f"**Source:** arXiv:2512.12818\n\n"
markdown += "---\n\n"

# Add the rest of the content
markdown += full_text

print(f"Writing to {output_path}...")
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(markdown)

# Get basic stats
word_count = len(full_text.split())
char_count = len(full_text)

print(f"\n✓ Extraction complete!")
print(f"  - Output: {output_path}")
print(f"  - Words: {word_count:,}")
print(f"  - Characters: {char_count:,}")
print(f"  - Pages: {len(pdf.pages)}")
