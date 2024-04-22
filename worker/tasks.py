from celery import Celery
from datetime import datetime
from sqlalchemy.orm import scoped_session
from google.cloud import storage
from google.oauth2 import service_account
from video_proc import edit_video
import os

from models import Session, Video, Status

app = Celery('tasks' , broker=os.getenv('BROKER_URL'))

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


        # # Create a temporary local file to download the video
        # temp_file_name = '/tmp/' + buket_filename  # Change this path as needed
        # source_blob.download_to_filename(temp_file_name)
        # print("Downloaded")

        file_name = os.path.join("/app/datos/", buket_filename)
        new_name = "edited_" + buket_filename
        file_name2 = os.path.join("/app/datos/", new_name) # Change this path as needed
        edit_video(file_name, logo_path , file_name2)
        print("Edited")
        
        # Upload the video with a different name
        # destination_bucket = client.bucket("test-buket-videos")  # You can change the destination bucket if needed
        # destination_blob = destination_bucket.blob(buket_filename)
        # destination_blob.upload_from_filename(temp_file_name2)
        # print("Uploaded")

        video.status = Status.CONVERTED
        db.commit()
        print("Commit")
    except Exception as e:
        print(e)
        db.rollback()


    return f"Video {buket_filename} processed"