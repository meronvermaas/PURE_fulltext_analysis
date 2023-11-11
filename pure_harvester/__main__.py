import pandas as pd
import json
import click
import os

from pure_harvester.outputs_api import get_outputs
from pure_harvester.datasets_api import get_dataset_meta


@click.command()
@click.option("--download", default=False, type=bool, help="Download publications")
@click.option("--key", prompt="Pure API key", help="Pure API key", hide_input=True)
@click.argument('published_after', default='2022-01-01')
@click.argument('outdir', default='output')
def pure_data(**kwargs):
    """
    [PUBLISHED_AFTER] Harvest publications after date (default: published_after=2022-01-01)

    [OUTDIR] Output directory name (default: outdir=output)
    """

    if 'outdir' in kwargs:
        if not os.path.exists(kwargs.get('outdir')):
            os.makedirs(kwargs.get('outdir'), exist_ok=True)
    # get metadata (and download publications)
    metadata = get_outputs(download=kwargs.get('download'),
                           download_path=kwargs.get('outdir'),
                           api_key=kwargs.get('key'),
                           published_after=kwargs.get('published_after'))
    with open(f'{kwargs.get("outdir")}/metadata.json', 'w') as f:
        f.write(json.dumps(metadata))
    # get datasets metadata
    datasets = []
    for pub in metadata:
        if pub['datasets']:
            pub_datasets = pub['datasets'].split('|')
            for dataset_uuid in pub_datasets:
                doi = get_dataset_meta(dataset_uuid, api_key=kwargs.get('key'))
                if doi:
                    datasets.append({
                        'pub_uuid': pub['uuid'],
                        'data_uuid': dataset_uuid,
                        'data_doi': doi
                    })
    with open(f'{kwargs.get("outdir")}/datasets.json', 'w') as f:
        f.write(json.dumps(datasets))
    # merge the two into dataframe
    df = pd.DataFrame(metadata).merge(pd.DataFrame(datasets),
                                      how='left', left_on='uuid', right_on='pub_uuid').drop(columns='pub_uuid')
    df.to_csv(f'{kwargs.get("outdir")}/merge.csv', index=False)


if __name__ == '__main__':
    pure_data()

