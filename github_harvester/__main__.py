import asyncio
import json
import re
import sys
import pandas as pd

import requests
from requests.auth import HTTPBasicAuth


# returns a list of contributor API URLs
async def scrape_single_repo(owner, repo, github_username=None, github_key=None):
    api_url = 'https://api.github.com/repos/{}/{}/stats/contributors'.format(owner, repo)

    basic = None
    if github_username is not None and github_key is not None:
        basic = HTTPBasicAuth(github_username, github_key)

    # we often get a 202 status code, which means GitHub is still processing the request
    # and we should check back later
    response = None
    loop = asyncio.get_event_loop()
    for i in range(10):
        response = await loop.run_in_executor(None, lambda: requests.get(api_url, auth=basic))
        if response.status_code == 200:
            break

        if response.status_code == 204 or response.status_code == 404:
            return None

        await asyncio.sleep(3)

    if response.status_code != 200:
        return None

    author_urls = []
    response_json = response.json()
    for author in response_json:
        author_urls.append(author['author']['url'])

    return author_urls


async def scrape_github(github_repos, github_username=None, github_key=None):
    task_per_repo = {}
    for repo in github_repos:
        key = '{}/{}'.format(repo[0], repo[1])
        task_per_repo[key] = asyncio.create_task(scrape_single_repo(repo[0], repo[1], github_username, github_key))

    author_urls_per_repo = {}
    for item in task_per_repo.items():
        key = item[0]
        author_url_list = await item[1]
        author_urls_per_repo[key] = author_url_list

    return author_urls_per_repo


# This script should be called with the following arguments:
# 1. The location of the CSV file
# 2. The location of the output file you want to append the (JSON) data to
# 3. (Optionally, recommended for increased rate limits) your GitHub username
# 4. (Optionally, recommended for increased rate limits) your GitHub access token (https://github.com/settings/tokens)
#
# This script performs the following steps:
# 1. Extract GitHub URLs from the CSV file using a regular expression
# 2. Concurrently, using asyncio, scrape each GitHub repo for its contributors
# using the stats/contributors endpoint,
# see https://docs.github.com/en/rest/metrics/statistics?apiVersion=2022-11-28#get-all-contributor-commit-activity
# 3. From each contributor, save the API URL of that GitHub user which you can harvest later
# 4. Append the aggregated data to a JSON file
async def main():
    csv_location = sys.argv[1]
    output_location = sys.argv[2]
    github_username = sys.argv[3] if len(sys.argv) >= 5 else None
    github_api_key = sys.argv[4] if len(sys.argv) >= 5 else None

    lines = pd.read_csv(csv_location)
    lines = lines['github_url']

    github_repo_regex = 'github\\.com/([a-zA-Z0-9_-]+)/([a-zA-Z0-9_-]+)/?'

    github_repos = []

    for line in lines:
        matches = re.findall(github_repo_regex, line)

        for match in matches:
            github_repos.append(match)

    author_urls_per_repo = await scrape_github(github_repos, github_username, github_api_key)

    with open(output_location, 'a') as outputFile:
        outputFile.write(json.dumps(author_urls_per_repo, indent='\t'))

if __name__ == '__main__':
    asyncio.run(main())
