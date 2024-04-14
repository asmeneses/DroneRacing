from celery import Celery
from datetime import datetime
from sqlalchemy.orm import scoped_session
import os

from models import Session, Video, Status

app = Celery('tasks' , broker=os.getenv('BROKER_URL'))
# app.config_from_object('celeryconfig')

@app.task(bind=True)
def upload_video(self, video_path, video_id):
    db = scoped_session(Session)
    try:
        video = db.query(Video).filter_by(id=video_id).first()
        video.status = Status.UPLOADING
        db.commit()

        # TODO: Implement the upload_video_file function
        # upload_video_file(video_path)

        video.status = Status.UPLOADED
        db.commit()
    except Exception as e:
        print(e)
        db.rollback()
    # finally:
    #     db_session.remove()