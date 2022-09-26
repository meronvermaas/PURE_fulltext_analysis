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
@click.option("--grouping_list", '-gl', default=None, multiple=True, type=str,
              help="Plot grouping by this parameter, e.g., pub_year or 'organisations_names'")
@click.argument('indir', default='output')
@click.argument('outdir', default='papertext_output')
@click.argument('keywords', type=list,
                default=[('github', 'gitlab', 'bitbucket', 'subversion', 'apache allura', 'gogs', 'gitea'),
                         ('r core team', 'r-project', 'python', 'html', 'css', 'java', 'javascript', 'swift', 'c #',
                          'c++', 'golang', 'php', 'typescript', 'stata', 'spss', 'scala', 'shell', 'powershell', 'perl',
                          'haskell', 'kotlin', 'visual basic', 'sql', 'matlab', 'excel', ['lua', 'programming'],
                          'ruby', ['bezanson', 'julia'], 'arcgis'),
                         ('bazis', 'hpc', 'high-performance computing', ['snellius', 'surf'], ['lisa', 'surf'],
                          'peter stol', 'p. stol', 'itvo', 'diebert van rhijn', 'd. van rhijn', 'high-end computing', 'nwo', 'erc')])
def pure_text(**kwargs):
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

    if kwargs.get('text_scrape_only') and os.path.exists(f'{kwargs.get("outdir")}/merge_text.csv'):
        full_text_papers = pd.read_csv(f'{kwargs.get("outdir")}/merge_text.csv')
    else:
        # get metadata (and download publications)
        full_text_papers = get_text(fulltext_download_path=kwargs.get('indir'),
                                    affiliation=kwargs.get('affiliation'))
        full_text_papers.to_csv(f'{kwargs.get("outdir")}/merge_text.csv', index=False)

    keywords_counted_papers = get_text_keywords(full_text_papers=full_text_papers,
                                                keywords=kwargs.get("keywords"))
    keywords_counted_papers.to_csv(f'{kwargs.get("outdir")}/keywords_in_text.csv', index=False)

    plot_keywords(outdir=kwargs.get("outdir"),
                  keywords_stats=keywords_counted_papers,
                  keywords=kwargs.get("keywords"),
                  grouping_list=list(kwargs.get("grouping_list")))


if __name__ == '__main__':
    pure_text()
