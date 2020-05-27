create-env:
	python -m venv env

activate-env:
	source env/Scripts/activate

install-env:
	pip install -r requirements.txt

# Convert multipage PDFs to single page files
splitpages: output/pdfpages pdf2pages.py
output/pdfpages:
	mkdir -p output/pdfpages
	python pdf2pages.py pdfs output/pdfpages

# Extract images from single page PDFs
extractimages: output/pageimages
output/pageimages: output/pdfpages pdfpage2image.py
	mkdir -p output/pageimages
	python pdfpage2image.py output/pdfpages output/pageimages

# OCR each individual page
extracttext: output/pagetexts
output/pagetexts: output/pageimages pytesseractwrapper.py
	mkdir -p output/pagetexts
	python pytesseractwrapper.py output/pageimages output/pagetexts

# Collate separate OCR datafiles into a single file
collatedata: output/namedata.txt
output/namedata.txt: pagetext2dataframe.py output/pagetexts
	python pagetext2dataframe.py output/pagetexts output/namedata.txt

matchnames: output/matchednamedata.txt
output/matchednamedata.txt: matchnames.py output/namedata.txt data/ipniWebName.csv.xz
	python matchnames.py output/namedata.txt data/ipniWebName.csv.xz output/matchednamedata.txt

excel: output/matchednamedata.xlsx
output/matchednamedata.xlsx: matchednames2excel.py output/matchednamedata.txt
	python matchednames2excel.py output/matchednamedata.txt output/matchednamedata.xlsx

clean:
	rm -rf output

sterilise:
	rm -rf output
	rm -rf data

# Download data from IPNI used for name matching
ipnidata: data/ipniWebName.csv.xz

data/ipniWebName.csv.xz:
	mkdir -p data
	wget -O data/ipniWebName.csv.xz https://storage.googleapis.com/ipni-data/ipniWebName.csv.xz