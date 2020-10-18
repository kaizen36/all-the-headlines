from google.cloud import storage
import csv
import os


def download_data():
    client = storage.Client()
    bucket_name = os.environ["GCS_BUCKET"]
    file_list = [f.name for f in client.list_blobs(bucket_name)]
    most_recent_file = sorted(file_list)[-1]
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(most_recent_file)
    blob.download_to_filename("static/data.csv")


def get_data():
    with open("static/data.csv") as f:
        reader = csv.DictReader(f, delimiter=",", quotechar='"')
        for row in reader:
            yield row


if __name__ == "__main__":
    download_data()
    data = get_data()
    print(data)
