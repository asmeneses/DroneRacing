from flask import Blueprint, request, jsonify
from sqlalchemy.orm import scoped_session
import json
import base64
from google.cloud import storage
from .video_proc import edit_video

from .models import Status, Video
from .models import Session

worker = Blueprint('worker', __name__)

@worker.route('/')
def index():
    return jsonify({'message': 'Welcome to the Worker API'}), 200

@worker.route('/process', methods=['POST'])
def process_video():

    data = request.get_json()

    if "message" not in data:
        return jsonify({"error": "Invalid request"}), 400
    
    message = data["message"]
    
    message_data = message.get('data', None)

    if not message_data:
        return jsonify({"error": "No message data received"}), 400
    
    message_data_decoded = base64.b64decode(message_data).decode("utf-8")

    message_data_dict = json.loads(message_data_decoded)

    video_id = message_data_dict["videoId"]
    buket_filename = message_data_dict["buketFilename"]

    db = scoped_session(Session)
    logo_path = "./assets/logo.png"
    print("INIT")

    print(video_id)
    print(buket_filename)

    try:
        video = db.query(Video).filter_by(id=video_id).first()
        client = storage.Client()


        # Get the source bucket and blob
        source_bucket = client.bucket("test-buket-videos1")
        source_blob = source_bucket.blob(buket_filename)


        # Create a temporary local file to download the video
        temp_file_name = '/tmp/' + buket_filename  # Change this path as needed
        temp_file_name2 = '/tmp/' + buket_filename + "-edited.mp4"  # Change this path as needed
        source_blob.download_to_filename(temp_file_name)
        print("Downloaded")

        # file_name = os.path.join("/app/datos/", buket_filename)
        # new_name = "edited_" + buket_filename
        # file_name2 = os.path.join("/app/datos/", new_name) # Change this path as needed
        edit_video(temp_file_name, logo_path , temp_file_name2)
        print("Edited")
        
        # Upload the video with a different name
        destination_bucket = client.bucket("test-buket-videos1")  # You can change the destination bucket if needed
        destination_blob = destination_bucket.blob(buket_filename)
        destination_blob.upload_from_filename(temp_file_name2)
        print("Uploaded")

        video.status = Status.CONVERTED
        db.commit()
        print("Commit")

    except Exception as e:
        print(e)
        db.rollback()
        return jsonify({"error": "Unable to process video"}), 500

    return jsonify({'status': 'video processed', 'video_id': video.id}), 201