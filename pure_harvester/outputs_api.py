import requests
import json
import os
import math


def get_outputs(download, download_path, api_key, pure_url, published_after='2022-01-01', size=100, offset=0):
    # get number of records and cycles
    url_ro = pure_url+'research-outputs?'
    result = do_request(size, offset, api_key, published_after, url_ro)
    no_records = (result['count'])
    cycles = (math.ceil(no_records / size))
    metadata = []

    for r in range(cycles):
        offset += size
        result = do_request(size, offset, api_key, published_after, url_ro)
        for count, item in enumerate(result['items']):
            if 'electronicVersions' in item:
                for eversion in item['electronicVersions']:
                    if 'file' in eversion:
                        if download and 'fileURL' in eversion['file']:
                            req_url = requests.get(eversion['file']['fileURL'])
                            pub_path = os.path.join(download_path, item['uuid'])
                            os.makedirs(pub_path, exist_ok=True)
                            # check length path + filename, should not exceed 255 characters
                            path_length = len(f'{os.getcwd()}/{pub_path}/{eversion["file"]["fileName"]}')
                            if path_length > 255:
                                eversion["file"]["fileName"] = eversion["file"]["fileName"][path_length-255:]
                            # download file
                            print(pub_path, eversion["file"]["fileName"], f'{pub_path}/{eversion["file"]["fileName"]}')
                            with open(f'{pub_path}/{eversion["file"]["fileName"].rsplit("/", 1)[-1]}', 'wb') as f:
                                f.write(req_url.content)
                        # metadata: organisations, year, uuids (datasets)
                        # organisations
                        organisations_str = None
                        organisations_names_str = None
                        if 'organisationalUnits' in item:
                            organisations = []
                            organisations_names = []
                            for organisation in item['organisationalUnits']:
                                # contains external organisations as well
                                organisations.append(organisation['uuid'])
                                organisations_names.append(organisation['name']['text'][0]['value'])
                            organisations_str = '|'.join(organisations)
                            organisations_names_str = '|'.join(organisations_names)
                        # year
                        pub_year = ''
                        epub_year = ''
                        for pubstatus in item['publicationStatuses']:
                            pubstatus_text = None
                            for text in pubstatus['publicationStatus']['term']['text']:
                                if text['locale'] == 'en_GB':
                                    pubstatus_text = text['value']
                            if pubstatus_text == 'E-pub ahead of print':
                                epub_year = pubstatus['publicationDate']['year']
                            elif pubstatus_text == 'Published':
                                pub_year = pubstatus['publicationDate']['year']
                        # datasets
                        datasets_str = None
                        if 'relatedDataSets' in item:
                            datasets = []
                            for dataset in item['relatedDataSets']:
                                datasets.append(dataset['uuid'])
                            datasets_str = '|'.join(datasets)
                        metadata.append({'uuid': item['uuid'],
                                         'pub_year': pub_year,
                                         'epub_year': epub_year,
                                         'organisations': organisations_str,
                                         'organisations_names': organisations_names_str,
                                         'datasets': datasets_str})

    return metadata


def do_request(size, offset, api_key, published_after, url_ro):
    success = False
    retry = 0
    result = None
    while not success and retry < 3:
        data = json.dumps({'publishedAfterDate': published_after})
        response = requests.post(url_ro,
                                 headers={"Content-Type": "application/json", 'Accept': 'application/json'},
                                 params={'size': size, 'offset': offset, 'apiKey': api_key},
                                 data=data)
        if response.status_code == 200:
            success = True

            # Check if the response's content type is JSON
            if response.headers.get('Content-Type') == 'application/json':
                try:
                    response_text = response.text
                    decoder = json.JSONDecoder()
                    pos = 0
                    result, pos = decoder.raw_decode(response_text, pos)
                    #result = response.json()
                except requests.exceptions.JSONDecodeError as e:
                    print("JSON decoding error:", e)
                    #print("Response text:", response.text)
                    with open("response_debug.txt", "w", encoding="utf-8") as file:
                        file.write(response.text)
                    result = []  # Or handle as appropriate
            else:
                print("Unexpected content type:", response.headers.get('Content-Type'))
                result = []  # Or handle as appropriate

            # result = response.json()
        else:
            retry += 1
            print('API error, retrying')
    if not success:
        raise Exception('API failure')

    return result
