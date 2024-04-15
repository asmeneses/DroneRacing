from celery import Celery
from datetime import datetime
from sqlalchemy.orm import scoped_session
from google.cloud import storage
from google.oauth2 import service_account
from video_proc import edit_video
import os

from models import Session, Video, Status

app = Celery('tasks' , broker=os.getenv('BROKER_URL'))
# app.config_from_object('celeryconfig')

@app.task(bind=True)
def upload_video(self, video_id, buket_filename):
    db = scoped_session(Session)
    logo_path = "./assets/logo.png"
    print("INIT")
    try:
        video = db.query(Video).filter_by(id=video_id).first()
        client = storage.Client()

        # Get the source bucket and blob
        source_bucket = client.bucket("test-buket-videos")
        source_blob = source_bucket.blob(buket_filename)

        # Create a temporary local file to download the video
        temp_file_name = '/tmp/' + buket_filename  # Change this path as needed
        source_blob.download_to_filename(temp_file_name)
        print("Downloaded")


        new_name = "edited_" + buket_filename
        temp_file_name2 = '/tmp/' + new_name  # Change this path as needed
        edit_video(temp_file_name, logo_path , temp_file_name2)
        print("EDited")
        
        # Upload the video with a different name
        destination_bucket = client.bucket("test-buket-videos")  # You can change the destination bucket if needed
        destination_blob = destination_bucket.blob(buket_filename)
        destination_blob.upload_from_filename(temp_file_name2)
        print("Uploaded")

        video.status = Status.CONVERTED
        db.commit()
        print("Commit")
    except Exception as e:
        print(e)
        db.rollback()

    # Delete the temporary file
    os.remove(temp_file_name)

    return f"Video {buket_filename} processed"