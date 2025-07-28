\# PDF Outline Extractor



\## Overview

This solution extracts structured outlines (title and headings H1, H2, H3) from PDF documents and outputs them in JSON format.



\## Approach

1\. \*\*Title Extraction\*\*: First attempts to extract title from PDF metadata, then from the largest font text on the first page

2\. \*\*Text Processing\*\*: Uses pdfplumber to extract character-level formatting information

3\. \*\*Heading Detection\*\*: Combines multiple techniques:

&nbsp;  - Font size analysis to identify heading thresholds

&nbsp;  - Pattern matching for numbered headings (1., 1.1., 1.1.1.)

&nbsp;  - Bold text detection

&nbsp;  - Structural analysis



\## Libraries Used

\- \*\*pdfplumber\*\*: Character-level PDF text extraction with formatting

\- \*\*PyPDF2\*\*: PDF metadata extraction

\- \*\*re\*\*: Pattern matching for heading detection

\- \*\*json\*\*: Output formatting



\## Features

\- Handles various PDF layouts and font sizes

\- Detects numbered and unnumbered headings

\- Multilingual support through Unicode handling

\- Robust error handling

\- Efficient processing (under 10 seconds for 50-page PDFs)



\## Build and Run



\### Build Docker Image

```bash

docker build --platform linux/amd64 -t pdf-extractor:latest .

