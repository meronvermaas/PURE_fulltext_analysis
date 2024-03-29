import requests


def get_dataset_meta(uuid, api_key, pure_url):
    url_ds = pure_url+'datasets?'
    result = do_request(uuid, api_key, url_ds)
    doi = None
    if result:
        item = result['items'][0]
        doi = item.get('doi', None)
        if not doi:
            print('no doi for dataset', uuid)
    return doi


def do_request(uuid, api_key,url_ds):
    success = False
    retry = 0
    result = None
    while not success and retry < 3:
        response = requests.get(url_ds, headers={'Accept': 'application/json'},
                                params={'q': uuid, 'apiKey': api_key})
        if response.status_code == 200:
            success = True
            result = response.json()
        elif response.status_code == 404:
            success = True  # we cannot find the dataset
            print('could not find dataset', uuid)
        else:
            retry += 1
            print('API error, retrying')
    if not success:
        raise Exception('API failure')

    return result
