# aistudio-uk-school-predictions
[Ofsted](https://reports.ofsted.gov.uk/) publishes reports on school performances across the UK.
This repo contains 1) a scraper to pull reports from Ofsted's site, 2) Jupyter notebooks
that contain exploratory analysis to predict whether or not a school may be in danger of closing,
and 3) the code for an app where you can play with a live version of our classifier.
This project was made by the [Quartz AI Studio](https://qz.ai/) in collaboration with BBC data journalist Paul Bradshaw.

## Prequisites
Tika, the dependency that converts PDF files into text, requires Java to run. You can download
the latest version of Java through [Oracle](https://www.java.com/en/download/). Alternatively,
if you have a Mac, you can simply run `brew cask install java`.

To install all Python related dependencies, run `pip install -r requirements.txt`
for the Render app's dependencies and `pip install -r scraper_requirements.txt` for
the scraper's dependencies.

Download the school report data by running:
```
mkdir schools
aws s3 sync s3://qz-aistudio-jbfm-scratch/schools schools
```

## Scraper
Run `python scraper/scraper.py` if you'd like to scrape a set of new reports. You can also
scrape the addresses of schools and the publication dates of their inspection reports
in `scraper/get_addresses.py` and `scraper/get_dates.py` respectively.

## Machine Learning Analysis
Our exploratory analysis can be found in Jupyter notebooks in the `/nbs` directory.
If you'd like to get started quickly, we've provided sample CSVs with a total of 2,000 reports
under the `/data` directory. Here's a high level overview of the machine learning approaches we took:

- `uk-school-predictions.ipynb`: a scikit-learn approach using a [bag-of-words model](https://en.wikipedia.org/wiki/Bag-of-words_model) and a [Naive Bayes classifier](https://en.wikipedia.org/wiki/Naive_Bayes_classifier)
- `ukschools-fastai-tabtext.ipynb`: we tried accounting for additional meta-data
(dates and school names) in our corpus by combining [tabular](https://www.fast.ai/2018/04/29/categorical-embeddings/)
and [text](https://course.fast.ai/videos/?lesson=4) neural nets.
This approach was inspired by and used code from [this public repository](https://github.com/anhquan0412/fastai-tabular-text-demo).
- `last-report-final.ipynb`: this approach used fast.ai's library for NLP problems.
We took our corpus of reports to predict whether or not the report may be the final report
before the school closes. The dataset for this notebook is different because it required a
different target label. In the dataset, the final reports of closed schools were labeled `last`
and all schools were labeled `not_last`. You can view this dataset in `app/last_report_test_sample.csv`.

## Render App
To view the app locally, run `python app/server.py serve`.
