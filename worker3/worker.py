from google.cloud import pubsub_v1, storage
from flask import Flask, jsonify
import threading
import time
from models import Session, Video, Status
from sqlalchemy.orm import scoped_session
from video_proc import edit_video
import json
import os


# Initialize Flask app
app = Flask(__name__)

# Health check route
@app.route('/healthcheck', methods=['GET'])
def health_check():
    return jsonify(status='healthy'), 200

def upload_video(video_id, buket_filename):
    db = scoped_session(Session)
    logo_path = "./assets/logo.png"
    print("INIT")
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
        db.rollback()
        raise


    return f"Video {buket_filename} processed"

def callback(message):
    message_data = message.data.decode("utf-8")
    message_dict = json.loads(message_data)

    print(f"Received message: {message_dict}")
    video_id = message_dict["videoId"]
    buket_filename = message_dict["buketFilename"]
    upload_video(video_id, buket_filename)
    print(f"Processed message: {message_dict}")

    message.ack()

# Function to listen to Pub/Sub subscription
def listen_to_subscription(project_id, subscription_id):
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(project_id, subscription_id)

    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    print(f"Listening for messages on {subscription_path}...")

    try:
        streaming_pull_future.result()
    except Exception as e:
        print(f"Listening for messages on {subscription_path} threw an exception: {e}.")
        streaming_pull_future.cancel()

if __name__ == '__main__':
    project_id = 'soluciones-cloud-420918'
    subscription_id = 'videos-sub-pull-1'

    # Start Pub/Sub listener in a separate thread
    listener_thread = threading.Thread(target=listen_to_subscription, args=(project_id, subscription_id))
    listener_thread.start()

    # Start Flask app
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
