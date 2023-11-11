import pdfplumber
import pikepdf
from pdfminer.pdfdocument import PDFEncryptionError, PDFNoValidXRef
from pdfminer.pdfparser import PDFSyntaxError, PSEOF
import pandas as pd
import copy
import os


def get_text(fulltext_download_path, fulltext_output_path, affiliation=None):
    df = pd.read_csv(f'{fulltext_download_path}/merge.csv')
    df = df.drop_duplicates()
    df['paper_text'] = ""
    failed_pages = 0
    failed_pdfs = 0
    success_pdf = 0

    for subdir in next(os.walk(fulltext_download_path))[1]:
        # put all text in pdfs from a project in 1 single text string
        all_text = ""

        # Check if directory exists in merge.csv output from pure_harvester and for affiliation filtering
        if df[df['uuid'] == subdir].empty or (affiliation != df[df['uuid'] == subdir]['organisations_names'].values[0] and affiliation is not None):
            continue

        for file in os.listdir(os.path.join(fulltext_download_path, subdir)):
            if file.endswith('.pdf'):
                try:
                    pdf = pdfplumber.open(os.path.join(fulltext_download_path, subdir, file))
                except PDFEncryptionError:
                    pdf = pikepdf.open(os.path.join(fulltext_download_path, subdir, file))
                    pdf.save(os.path.join(fulltext_download_path, subdir, file[:-4] + '_unencrypted.pdf'))
                    pdf = pdfplumber.open(os.path.join(fulltext_download_path, subdir, file[:-4] + '_unencrypted.pdf'))
                except (PDFSyntaxError, PDFNoValidXRef, PSEOF):
                    print('this PDF could not be read, skipping to next one',
                          os.path.join(fulltext_download_path, subdir, file))
                    failed_pdfs += 1
                    continue

                print(os.path.join(fulltext_download_path, subdir, file))
                for pdf_page in pdf.pages:
                    try:
                        single_page_text = pdf_page.extract_text(x_tolerance=1)
                    except:  # this should be made less broad
                        failed_pages += 1
                        single_page_text = ""
                    # In some cases, a massive pdf might lead to memory issues
                    # TODO write out in chunks, for now we will skip part of these
                    try:
                        all_text = all_text + ' ' + single_page_text
                    except MemoryError:
                        continue
                pdf.close()

        df2 = copy.deepcopy(df.loc[df['uuid'] == subdir])
        df2['paper_text'] = all_text
        if not os.path.isfile(f'{fulltext_output_path}/merge_text.csv'):
            df2.to_csv(f'{fulltext_output_path}/merge_text.csv', mode='a', index=False, header=True, encoding="utf8")
        else:
            df2.to_csv(f'{fulltext_output_path}/merge_text.csv', mode='a', index=False, header=False, encoding="utf8")
        success_pdf += 1

    print('Imported ', success_pdf, ' PDFs successfully')
    print('Failed to import ', failed_pdfs, ' PDFs')
    print('Failed to read ', failed_pages, ' pages')
