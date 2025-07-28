\# Adobe India Hackathon - Round 1A: Connecting the Dots



\## Challenge Theme: Understand Your Document



This repository contains the solution for Round 1A of the Adobe India Hackathon, focusing on extracting a structured outline (Title, H1, H2, H3) from PDF documents and outputting it in a specified JSON format.



\## Approach



Our solution is implemented in Python and utilizes the `PyMuPDF` library for efficient and detailed PDF parsing. The core logic resides in `src/pdf\_processor.py`.



1\.  \*\*PDF Parsing\*\*: We use `PyMuPDF` (imported as `fitz`) to open and read PDF documents. This library allows us to access text content block by block, along with valuable metadata like font sizes, bolding flags, and positional information.



2\.  \*\*Title Extraction\*\*:

&nbsp;   \* The primary attempt is to retrieve the document title from the PDF's metadata. This is the most reliable method when available.

&nbsp;   \* As a fallback, if metadata is absent or insufficient, we apply a heuristic: we scan the text blocks on the first page, looking for large, bold text typically positioned at the top, which is a common indicator of a document title.



3\.  \*\*Heading (H1, H2, H3) Detection\*\*:

&nbsp;   This is the most critical and complex part, relying on a combination of heuristics:

&nbsp;   \* \*\*Font Size Analysis\*\*: We first iterate through the entire document to collect all unique font sizes. By sorting these, we can identify potentially significant font sizes that might correspond to headings (e.g., the largest distinct sizes after the main title). A basic mapping is applied where larger font sizes are tentatively assigned higher heading levels (H1, H2, H3).

&nbsp;   \* \*\*Font Style (Boldness)\*\*: Text marked as bold is given higher consideration as a heading, especially when combined with font size clues.

&nbsp;   \* \*\*Text Length\*\*: Headings are generally concise. We filter out very long lines of text to avoid misclassifying body paragraphs as headings.

&nbsp;   \* \*\*Hierarchical Order\*\*: The extracted headings are stored along with their page numbers. While the current heuristic-based mapping is simple, a more advanced solution would involve analyzing relative positions, indentation, and consistent numbering patterns (e.g., "1. Introduction", "1.1. Subtopic") to establish a robust hierarchy.

&nbsp;   \* \*\*Deduplication\*\*: After initial extraction, a basic deduplication step removes identical heading entries (same level, text, and page) that might arise from parsing nuances.

&nbsp;   \* \*\*Sorting\*\*: The final outline is sorted by page number and then by text to ensure a consistent and logical output order.



\## Models or Libraries Used



\* \*\*Python 3.9\*\*: The programming language used for the solution.

\* \*\*PyMuPDF (fitz)\*\*: Version `1.22.0`. This is the primary library for PDF parsing, chosen for its speed and comprehensive text extraction capabilities, including font information critical for heading detection.

\* \*\*`json`\*\*: Standard Python library for handling JSON data (output formatting).

\* \*\*`os`\*\*: Standard Python library for interacting with the file system (reading input files, creating output directories).



\## How to Build and Run Your Solution (for Documentation Purposes)



These instructions are for local testing and documentation. The hackathon platform will use its specific `docker build` and `docker run` commands as outlined in the challenge document.



1\.  \*\*Prerequisites\*\*:

&nbsp;   \* Docker installed on your system.

&nbsp;   \* Python 3.9+ (for local development, though Docker handles the environment).



2\.  \*\*Clone the Repository\*\*:

&nbsp;   ```bash

&nbsp;   git clone <your\_git\_repo\_url\_here>

&nbsp;   cd <your\_project\_directory\_name>

&nbsp;   ```



3\.  \*\*Prepare Input Files\*\*:

&nbsp;   Place your `.pdf` files that you want to process into the `input/` directory within this project's root. For example, copy `sample.pdf` here.



4\.  \*\*Build the Docker Image\*\*:

&nbsp;   Navigate to the root directory of your project (where `Dockerfile` is located) in your terminal and run:

&nbsp;   ```bash

&nbsp;   docker build --platform linux/amd64 -t mypdfoutlineextractor:latest .

&nbsp;   ```

&nbsp;   This command builds a Docker image named `mypdfoutlineextractor` with the tag `latest`. The `--platform linux/amd64` ensures compatibility with the specified architecture.



5\.  \*\*Run the Docker Container\*\*:

&nbsp;   After the image is built, you can run your solution. This command will execute your `main.py` script inside the container, processing PDFs from the mounted `input` directory and writing results to the mounted `output` directory.

&nbsp;   ```bash

&nbsp;   docker run --rm -v "$(pwd)/input:/app/input" -v "$(pwd)/output:/app/output" --network none mypdfoutlineextractor:latest

&nbsp;   ```

&nbsp;   \* `--rm`: Automatically removes the container once it exits.

&nbsp;   \* `-v "$(pwd)/input:/app/input"`: Mounts your local `input` directory to `/app/input` inside the container.

&nbsp;   \* `-v "$(pwd)/output:/app/output"`: Mounts your local `output` directory to `/app/output` inside the container.

&nbsp;   \* `--network none`: Ensures the container has no network access during execution, fulfilling a challenge constraint.

&nbsp;   \* `mypdfoutlineextractor:latest`: Specifies the image to run.



Upon successful execution, you will find the generated JSON outline files (e.g., `sample.json`) in your local `output/` directory.

