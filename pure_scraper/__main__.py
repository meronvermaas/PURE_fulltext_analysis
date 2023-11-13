import click
import os
import pandas as pd

from pure_scraper.pdf_converter import get_text
from pure_scraper.pdf_scraper import get_text_keywords
from pure_scraper.pdf_scraper import plot_keywords


@click.command()
@click.option("--affiliation", default=None, type=str, help="Affiliation of interest, type --affiliation=? for options")
@click.option("--text_scrape_only", default=False, type=bool, help="If the pdfs have been converted already, skip "
                                                                   "converting pdfs to save time, input True")
@click.option("--plot_only", default=False, type=bool, help="If the pdfs have been scraped already, you can only plot")
@click.option("--grouping_list", '-gl', default=None, multiple=True, type=str,
              help="Plot grouping by this parameter, e.g., pub_year or 'organisations_names'")
@click.argument('indir', default='output')
@click.argument('outdir', default='papertext_output')
@click.argument('keywords', default='keywords.txt')
def pure_text(**kwargs):
    """
    [INDIR] Input directory name, which is the output from the pure_harvester (default: indir=output)

    [OUTDIR] Output directory name (default: outdir=papertext_output)

    [KEYWORDS] Textfile with a list [] keywords of interest. (default: keywords=keywords.txt)
    """
    if 'outdir' in kwargs:
        if not os.path.exists(kwargs.get('outdir')):
            os.makedirs(kwargs.get('outdir'), exist_ok=True)
    if not os.path.exists(kwargs.get('indir')):
        raise ValueError('An existing directory where the pdfs are should be provided: --indir=DIRECTORY')

    if kwargs.get('affiliation') == '?':
        df = pd.read_csv(f'{kwargs.get("indir")}/merge.csv')
        print('Options are:')
        print(pd.unique(df['organisations_names']))
        return

    if (not kwargs.get('text_scrape_only') or not kwargs.get('plot_only')) and not os.path.exists(f'{kwargs.get("outdir")}/merge_text.csv'):
        # get metadata (and download publications)
        get_text(fulltext_download_path=kwargs.get('indir'),
                 fulltext_output_path=kwargs.get('outdir'),
                 affiliation=kwargs.get('affiliation'))
    keywords = eval(open(kwargs.get("keywords")).read())  # pickle.load(open(kwargs.get("keywords"), 'rb'))

    if not kwargs.get('plot_only') and not os.path.exists(f'{kwargs.get("outdir")}/keywords_in_text.csv'):
        full_text_papers = pd.read_csv(f'{kwargs.get("outdir")}/merge_text.csv')
        keywords_counted_papers = get_text_keywords(full_text_papers=full_text_papers,
                                                    keywords=keywords,
                                                    fulltext_output_path=kwargs.get("outdir"))
    else:
        keywords_counted_papers = pd.read_csv(f'{kwargs.get("outdir")}/keywords_in_text.csv')

    plot_keywords(outdir=kwargs.get("outdir"),
                  keywords_stats=keywords_counted_papers,
                  keywords=keywords,
                  grouping_list=list(kwargs.get("grouping_list")))


if __name__ == '__main__':
    pure_text()
