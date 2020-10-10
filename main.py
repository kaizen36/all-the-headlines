"""Wrapper around scraper/get_headlines.py for Google Cloud Function."""
from scraper.get_headlines import load_config, get_all_headlines
from pprint import pprint


def scrape(request) -> list:
    """HTTP Google Cloud Function."""
    config = load_config("scraper/config.yaml")
    results = get_all_headlines(config)
    results_to_dict = [dict(result._asdict()) for result in results if result is not None]
    return {"data": results_to_dict}


if __name__ == "__main__":
    output = scrape(None)
    pprint(output)
