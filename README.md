# aistudio-uk-school-predictions
[Ofsted](https://reports.ofsted.gov.uk/) publishes reports on school performances across the UK. This scraper pulls these reports from their site to build a corpus intended to predict school closures in the UK.

## Prequisites
Tika, the dependency that converts PDF files into text, requires Java to run. You can download the latest version of Java through [Oracle](https://www.java.com/en/download/). Alternatively, if you have a Mac, you can simply run `brew cask install java`.

To install all Python related dependencies, run `pip install -r requirements.txt`.

Download the school report data by running:
```
mkdir schools
aws s3 sync s3://qz-aistudio-jbfm-scratch/schools schools
```

## Running the Code
Run `python scraper.py` to get started.
