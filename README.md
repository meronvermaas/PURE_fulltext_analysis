# PURE_fulltext_analysis

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

If you downloaded all the fulltext papers, you can now search for keywords:

```
python -m pure_scraper
```

For options and usage:

```
python -m pure_scraper --help
```