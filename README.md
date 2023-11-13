# PURE_fulltext_analysis

## Abstract

This repository aims to evaluate how FAIR code repositories created by researchers of a specific institute (VU Amsterdam) are.
Since there is no overview available of code developed at the VU. The current code can be used to scrape fulltext papers within the CRIS system PURE by first downloading the papers and then searching for keywords and repositories in the text.

The code will be expanded to check if the author of repositories found in the fulltext are affiliated to the VU.
After determing this, the repositories can be scanned via https://github.com/fair-software/howfairis and https://github.com/KnowledgeCaptureAndDiscovery/somef

## How to use


Make sure you are working from the top directory of the cloned repository.
To install, run setup.py:

```
python setup.py
```

If you just want to download a list of the fulltext papers, run:

```
python -m pure_harvester
```

After which you will be prompted to insert in a PURE API key.
This outputs 3 files: 2 .json files with metadata on the datasets and the papers found, and 1 .csv with a merge of these two .json files.

Other options/arguments (e.g., ouput directory, published after a certain date) can be found by typing:

```
python -m pure_harvester --help
```

If you want to download the fulltext papers available on PURE, run:

```
python -m pure_harvester --download=True
```

This might take a while and some memory (depending on the amount of papers).

After you downloaded all the fulltext papers, you can search for keywords:

```
python -m pure_scraper
```

For options and usage:

```
python -m pure_scraper --help
```

If you want to rerun with a new set of keywords (but the same papers), run:


```
python -m pure_scraper --text_scrape_only=True
```

If your want to create different plots (without scraping the text, and for example some grouping by one of the columns the publication year):

```
python -m pure_scraper --plot_only=True --grouping_list=pub_year
```