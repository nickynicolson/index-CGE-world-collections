# index-CGE-world-collections
Data extraction from OCR-d typewritten index of the Cambridge (CGE) herbarium world collections

## Requirements

Python packages are specified in `requirements.txt`. 

System utility requirements include:
- make
- ghostscript - the `gswin64c` utility must be available on the path
- tesseract (accessed via pytesseract) this must be installed and in the path, ie accessible by typing `tesseract` at a command prompt.

## Process

1. Split originally supplied multi-page PDFs to single page per PDF file (`pdf2pages.py`)
1. Extract image from each single page PDF file (`pdfpage2image.py`)
1. OCR page image, store result in a text file (`pytesseractwrapper.py`)
1. Collate all OCR text into a single delimited file (`pagetext2dataframe.py`)
1. Extract name portion of each line and look up against IPNI (`matchnames.py`)
    Name matching is executed in three stages:
    - Stage 0 - name and author is found as an exact match in the IPNI dataset
    - Stage 1 - name is found as an exact match in the IPNI dataset, name and author ranked by string similarity and best match selected
    - Stage 2 - using the exact matches made in stage 0 above, a search window is defined in the IPNI dataset (utilising the alphabetical ordering of the source data). Candidates in this search window are ranked by string similarity and the best match selected.

A makefile handles dependencies between each step of the process, it can be initiated from a newly cloned repository with the command: `make matchnames`
