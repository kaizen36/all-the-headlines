import requests
from bs4 import BeautifulSoup
import sys
import os
import yaml
import datetime
import subprocess
import csv
import argparse
from collections import namedtuple
from urllib.parse import urlparse, urljoin
from google.cloud import storage
from joblib import Parallel, delayed


Result = namedtuple(
    "Result", ["extract_ts", "country", "homepage", "text", "article_url", "id"]
)


def clean_text(text: str) -> str:
    if isinstance(text, str):
        return text.lower().strip()
    else:
        return ""


def display_text(text: str) -> str:
    return text.strip()


def fetch_page(url: str, method: str = "requests") -> str:
    if method == "requests":
        return requests.get(url).text
    elif method == "curl":
        proc = subprocess.Popen(f"curl -s {url}".split(), stdout=subprocess.PIPE)
        out, _ = proc.communicate()
        return out


def get_base_url(url: str) -> str:
    """Removes the path from any url
    e.g. http://www.bbc.co.uk/news -> http://www.bbc.co.uk/
    """
    uri = urlparse(url)
    base_url = f"{uri.scheme}://{uri.netloc}/"
    return base_url


def extract_headline(
    homepage: str, method: str, headline: str, link: str
) -> (datetime.datetime, str, str):
    ts = datetime.datetime.now()

    contents = fetch_page(homepage, method=method)
    base_url = get_base_url(homepage)
    doc = BeautifulSoup(contents, "html.parser")

    # get headline
    top_headline = ""
    for h in doc.find_all(headline["arg"], headline["kwargs"]):
        h_try = h.get_text()
        # make sure headline has more than one word
        if len(h_try.split()) > 1:
            top_headline = h.get_text()
            break
    if not top_headline:
        raise ValueError(f"Did not manage to find a headline for {homepage}!")

    # get headline url
    url = ""
    for l in doc.find_all(link["arg"], link["kwargs"], href=True):
        link_text = clean_text(l.text) or clean_text(l.get("title"))
        if clean_text(top_headline) in link_text:
            url = urljoin(base_url, l["href"])
            break
    if not url:
        raise ValueError(f"Did not manage to find a url for {homepage}!")

    return ts, display_text(top_headline), url


def upload_file(bucket_name: str, local_file_name: str, upload_file_name: str) -> str:
    """Upload file to Google Cloud Storage."""
    print(f"Uploading file to GCS {local_file_name} -> gcs://{bucket_name}/{upload_file_name}")
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    bucket.blob(upload_file_name).upload_from_filename(local_file_name)
    print("Upload complete")


def print_headline(news_config: dict) -> (datetime.datetime, str, str):
    print(f"Getting the headline for {news_config['country']}")
    try:
        ts, headline, url = extract_headline(
            news_config["homepage"],
            news_config["method"],
            news_config["headline"],
            news_config["link"],
        )
    except Exception as err:
        print(err)
        return None
    else:
        print(f"The headline in {news_config['country']} is:")
        print(display_text(headline))
        print(f"Go to: {url}")
        print()
    return Result(ts, news_config["country"], news_config["homepage"], headline, url, news_config["id"])


def load_config(path: str) -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)["data"]


def write_results_to_csv(results: list) -> None:
    file_name = "test.csv"
    print(f"Writing results to {file_name}")
    with open(file_name, "w") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=results[0]._fields,
            delimiter=",",
            quotechar='"',
            quoting=csv.QUOTE_ALL,
        )
        writer.writeheader()

        for result in results:
            writer.writerow(result._asdict())

    return file_name


def parse_args(sys_args: list) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config", "-c", default="config.yaml", help="Config YAML file"
    )
    parser.add_argument(
        "--upload",
        "-u",
        action="store_true",
        default=False,
        help="Upload results to Google Cloud Storage",
    )
    args = parser.parse_args(sys_args)
    return args


def get_all_headlines(config: dict, async_request: bool = True) -> list:
    if async_request:
        return Parallel(n_jobs=10, prefer="threads")(
            delayed(print_headline)(c) for c in config
        )
    else:
        return [print_headline(c) for c in config]


def main(args: argparse.Namespace) -> None:
    config = load_config(args.config)

    results = get_all_headlines(config)

    # filter out websites that failed to scrape
    results = [r for r in results if r]

    print("**********************************************")

    file_name = write_results_to_csv(results)

    if args.upload:
        bucket_name = os.environ["GCS_BUCKET"]
        upload_file_name = datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + ".csv"
        upload_file(bucket_name, file_name, upload_file_name)
        file_name = upload_file_name

    return file_name


if __name__ == "__main__":

    args = parse_args(sys.argv[1:])
    main(args)
