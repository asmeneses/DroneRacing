from oauth2client.service_account import ServiceAccountCredentials
from google.cloud import storage

def upload_to_gcs(filename, file):
    client = storage.Client()

    # Upload the file to Google Cloud Storage
    bucket_name = 'test-buket-videos'
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(filename)
    blob.upload_from_string(file.read(), content_type=file.content_type)