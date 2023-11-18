# PURE_fulltext_analysis

## Abstract

This repository aims to evaluate how FAIR code repositories created by researchers of a specific institute (VU Amsterdam) are.
Since there is no overview available of code developed at the VU. The current code can be used to scrape fulltext papers within the CRIS system PURE by first downloading the papers and then searching for keywords and repositories in the text.

The code will be expanded to check if the author of repositories found in the fulltext are affiliated to the VU.
After determing this, the repositories can be scanned via https://github.com/fair-software/howfairis and https://github.com/KnowledgeCaptureAndDiscovery/somef

## How to use

### Setting up

Make sure you are working from the top directory of the cloned repository.
To install, run setup.py:

```
python setup.py
```

### Downloading fulltext PDFs from PURE

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
Note that the default PURE instance is from the VU. If you want to try another institute (not yet tested), the url can be adjusted.

If you want to download the fulltext papers available on PURE, run:

```
python -m pure_harvester --download=True
```

This might take a while and some memory (depending on the amount of papers).

### Looking for keywords in the fulltext PDFs

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

If your want to create different plots (without scraping the text, and for example some grouping by one of the columns, in this case the publication year):

```
python -m pure_scraper --plot_only=True --grouping_list=pub_year
```

### Downloading collaborators from GitHub

In the output from the scraper, there will be a list of github repositories that were mentioned in the papers.
You can harvest GitHub API urls of all collaborators of each of these repositories by running:

```
python -m github_harvester PATH_TO_CSV_WITH_URLS OUTPUTPATH/FILE.json
```

Two more inputs are optional (but recommended to improve GitHub API rate limits). For more information you can type:

```
python -m github_harvester help
```

### Checking for affiliation (or something else)

Now we can check if our university is mentioned in the github user's metadata:

```
python -m github_scraper OUTPUTPATH/FILE.json OUTPUTPATH/METADATAFILE.json None None KEYWORD1 KEYWORD2 KEYWORD3
```

The two empty inputs are optional (but recommended to improve GitHub API rate limits). For more information you can type:

```
python -m github_scraper help
```

Two output files will be created:

- a .json for each collaborator indicating which keywords were found in the GitHub metadata
- a [...]_user_metadata.json with the metadata of each collaborator (to be used in further analyses)