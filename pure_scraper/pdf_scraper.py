import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from nltk.tokenize import word_tokenize
from nltk.text import Text


def get_text_keywords(full_text_papers, keywords, fulltext_output_path):
    # fill papers that were not converted with '' so tokenize works for all rows
    full_text_papers.paper_text = full_text_papers.paper_text.fillna('')
    # tokenize all texts first (split in single words and remove punctuation)
    full_text_papers['paper_text_tokenized'] = full_text_papers['paper_text'].apply(word_tokenize)
    # loop over the list of keyword groups
    for grouped_keywords in keywords:
        # loop over the keywords in the groups
        for keyword in grouped_keywords:
            # create new column
            if isinstance(keyword, list):
                if '&'.join(keyword) not in full_text_papers.columns:
                    column_name = '&'.join(keyword)
                    full_text_papers[column_name] = False
            else:
                if keyword not in full_text_papers.columns:
                    column_name = keyword
                    full_text_papers[column_name] = False
            # loop over each paper
            for idx in range(len(full_text_papers.paper_text_tokenized)):
                # For version control, often links are reported which are missed by nltk concordance,
                # so it is addressed in the else statement.
                if 'github' not in grouped_keywords:
                    text = Text(full_text_papers['paper_text_tokenized'][idx])
                    if isinstance(keyword, str):
                        keyword_occurrence = text.concordance_list(keyword.split())
                        if len(keyword_occurrence) > 0:
                            full_text_papers.loc[idx, column_name] = True
                    elif isinstance(keyword, list):
                        kw_bool = []
                        for kw in keyword:
                            keyword_occurrence = text.concordance_list(kw.split())
                            kw_bool.append(len(keyword_occurrence))
                        if all(kw_bool):
                            full_text_papers.loc[idx, column_name] = True
                        # TODO export the context around the found keywords
                        #  (already saved in keyword_occurrence list for the str case)
                # Search a bit broader with "substring in string" in the case of version control keywords
                else:
                    if any(keyword.lower() in token.lower() for token in full_text_papers['paper_text_tokenized'][idx]):
                        full_text_papers.loc[idx, column_name] = True
                        # search for links/presence of version control
                        # by checking .VERSIONCONTROL. and //VERSIONCONTROL using IN
                        for token in full_text_papers['paper_text_tokenized'][idx]:
                            if ('.' + keyword + '.' in token) or ('//' + keyword in token):
                                url_col_name = column_name + '_url'
                                if url_col_name not in full_text_papers.columns:
                                    full_text_papers[url_col_name] = np.empty((len(full_text_papers), 0)).tolist()
                                if token[0:2] == '//':
                                    token = token[2:]
                                full_text_papers.loc[idx, url_col_name].append(token)

    # Check if papers with data_doi metadata is mentioned in paper
    full_text_papers['data_doi_in_text'] = False
    for idx in full_text_papers[full_text_papers.data_doi.notna()].index:
        if full_text_papers.iloc[idx].data_doi.lower() in full_text_papers.iloc[idx].paper_text.lower():
            full_text_papers.iloc[idx, -1] = True

    #  remove pdf text from this dataframe to make it a bit lighter
    full_text_papers.drop('paper_text', axis=1, inplace=True)
    full_text_papers.drop('paper_text_tokenized', axis=1, inplace=True)

    full_text_papers.to_csv(f'{fulltext_output_path}/keywords_in_text.csv', index=False)


def plot_keywords(outdir, keywords_stats, keywords, grouping_list):
    # create dataframe with number of papers where keyword is mentioned for each group of keywords
    fig_counter = 1
    for grouped_keywords in keywords:
        column_names = []
        for keyword in grouped_keywords:
            if isinstance(keyword, str):
                column_names.append(keyword)
            elif isinstance(keyword, list):
                column_names.append('&'.join(keyword))
        if grouping_list:
            count_per_keyword = keywords_stats.groupby(grouping_list, dropna=False)[column_names].sum()
        else:
            count_per_keyword = keywords_stats[column_names].sum()

        # plot the number of occurrences per keyword
        if not grouping_list:
            ax = count_per_keyword.T.plot(kind='bar')
        else:
            # only show legend labels of keywords with at least 1 occurrence and stacked bar to make figure more compact
            df = count_per_keyword.astype(int)[(count_per_keyword.astype(int) > 0).any(axis=1)]
            rng = np.arange(len(df.T.columns)) / (len(df.T.columns))
            colors = plt.cm.gist_ncar(rng)
            ax = df.T.plot(kind='bar', stacked=True, color=colors)
            ax.legend(bbox_to_anchor=(1.0, 1.0))

        ax.set_title(str(len(keywords_stats)) + ' papers between year ' + str(int(keywords_stats.pub_year.min()))
                     + ' and ' + str(int(keywords_stats.pub_year.max())), color='black')

        if not grouping_list:
            for p in ax.patches:
                ax.annotate(str(int(p.get_height())), (p.get_x() + p.get_width() / 2., p.get_height()),
                            ha='center', va='center', xytext=(0, 5), textcoords='offset points')
        fig = ax.get_figure()
        if not grouping_list:
            filename = "figure" + str(fig_counter) + ".pdf"
        else:
            filename = "figure" + str(fig_counter) + "_groupby_" + str(grouping_list) + ".pdf"
        fig.savefig(outdir + "/" + filename, bbox_inches="tight")
        fig_counter += 1
        plt.close()

        data_doi_summary = pd.DataFrame([keywords_stats.data_doi.isna().sum(),
                                         keywords_stats.data_doi.notna().sum(),
                                         keywords_stats['data_doi_in_text'].sum()],
                                        index=['No dataset DOI metadata', 'Dataset DOI metadata',
                                               'Dataset DOI in text'])
        fig, ax = plt.subplots()
        # hide axes
        fig.patch.set_visible(False)
        ax.axis('off')
        ax.axis('tight')
        ax.table(cellText=data_doi_summary.T.values, colLabels=data_doi_summary.T.columns, loc='center',
                 cellLoc='center')
        fig.savefig(outdir + "/dataset_doi_numbers.pdf", bbox_inches="tight")
        plt.close()
