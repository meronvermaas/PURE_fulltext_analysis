import requests
import json
import asyncio
import sys
from requests.auth import HTTPBasicAuth
import aiohttp


async def get_github_user_metadata(session, api_url, username, token):
    if username and token:
        basic_auth = HTTPBasicAuth(username, token)

        # GitHub often returns a 202 status code, indicating the request is still processing
        # Check back multiple times before giving up
        for _ in range(10):
            response = await loop.run_in_executor(None, lambda: requests.get(api_url, auth=basic_auth))

            if response.status_code == 200:
                return await loop.run_in_executor(None, response.json)

            if response.status_code == 204 or response.status_code == 404:
                return None

            await asyncio.sleep(3)

    else:
        response = await session.get(api_url)

        if response.status == 200:
            return await loop.run_in_executor(None, response.json)
        else:
            print(f"Error: Unable to fetch data for URL {api_url}, status code: {response.status}")
            return None


async def check_keywords_in_metadata(session, user_url, keywords, username, token, output_file_path):
    user_metadata = await get_github_user_metadata(session, user_url, username, token)

    if user_metadata is not None:
        result = {}
        for keyword in keywords:
            result[keyword] = check_keyword_in_metadata_sync(user_metadata, keyword)

        # Append the metadata to the common JSON file
        with open(output_file_path[:-5] + "_user_metadata.json", 'a') as user_metadata_file:
            json.dump({user_url: user_metadata}, user_metadata_file, indent=2)
            user_metadata_file.write(',\n')  # Add a comma and newline for separating entries

        return result
    else:
        print(f"Error fetching metadata for user in URL '{user_url}'.")
        return None


def check_keyword_in_metadata_sync(metadata, keyword):
    if metadata is not None:
        for key, value in metadata.items():
            if isinstance(value, str) and keyword.lower() in value.lower():
                return True
        return False
    else:
        return False


# This script should be called with the following arguments:
# 1. The location of the JSON file
# 2. The location of the output file you want to write the GitHub metadata to
# 3. (Optionally, recommended for increased rate limits) your GitHub username
# 4. (Optionally, recommended for increased rate limits) your GitHub access token (https://github.com/settings/tokens)
# 5. Keywords that should be checked for in the GitHub metadata
#
# The script performs the following steps:
# 1. Import GitHub API URLs from the JSON file
# 2. Concurrently, using asyncio, scrape each GitHub repo for its contributors
# using the stats/contributors endpoint,
# see https://docs.github.com/en/rest/metrics/statistics?apiVersion=2022-11-28#get-all-contributor-commit-activity
# 3. From each contributor, save if the keyword occurs in the metadata of each contributor
# 4. Write the aggregated data to 2 JSON files, one containing if keywords are present, one with the metadata
async def main():
    if len(sys.argv) != 1 and sys.argv[1] == 'help':
        help(sys.modules['__main__'])
        return

    file_path = sys.argv[1] if len(sys.argv) > 1 else input("Enter the path to the JSON file: ")
    output_file_path = sys.argv[2] if len(sys.argv) > 2 else input("Enter the path to the output file: ")
    username = sys.argv[3] if len(sys.argv) > 3 else input("Enter your GitHub username (press Enter to skip): ")
    token = sys.argv[4] if len(sys.argv) > 4 else input("Enter your GitHub token (press Enter to skip): ")

    with open(file_path, 'r') as file:
        data = json.load(file)

    keywords = sys.argv[5:] if len(sys.argv) > 5 else input(
        "Enter keywords to search in metadata (separated by space): ").split()

    async with aiohttp.ClientSession() as session:
        results = {}
        for repo, user_urls in data.items():
            if user_urls is None:
                continue
            print(f"Checking repository: {repo}")
            for user_url in user_urls:
                task = check_keywords_in_metadata(session, user_url, keywords, username, token, output_file_path)
                results[f"{repo}_{user_url}"] = await task

        # Write the results to a JSON file
        with open(output_file_path, 'w') as output_file:
            json.dump(results, output_file, indent=2)

        # Read the contents of the file and create a list
        with open(output_file_path[:-5] + "_user_metadata.json", 'r') as user_metadata_file:
            lines = user_metadata_file.readlines()

        # Rewrite the file with proper list formatting
        with open(output_file_path[:-5] + "_user_metadata.json", 'w') as user_metadata_file:
            user_metadata_file.write("[\n")
            user_metadata_file.writelines(lines[:-1])  # Skip the last comma
            user_metadata_file.write("}]\n")

        print(f"Results written to: {output_file_path}")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
