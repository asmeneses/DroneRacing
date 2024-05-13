from google.cloud import pubsub_v1
from sqlalchemy.orm import scoped_session
from models import Session, Video, Status
from video_proc import edit_video
import json
from google.cloud import storage

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


project_id = "soluciones-cloud-420918"
subscription_id = "videos-sub-pull-1"

# Initialize a subscriber client
subscriber = pubsub_v1.SubscriberClient()

# Define the subscription path
subscription_path = subscriber.subscription_path(project_id, subscription_id)

# Define callback function
def callback(message):
    message_data = message.data.decode("utf-8")
    message_dict = json.loads(message_data)

    print(f"Received message: {message_dict}")
    video_id = message_dict["videoId"]
    buket_filename = message_dict["buketFilename"]
    upload_video(video_id, buket_filename)
    print(f"Processed message: {message_dict}")

    message.ack()

# Subscribe to the topic
subscriber.subscribe(subscription_path, callback=callback)

# Keep the main thread alive
print(f"Listening for messages on {subscription_path}...")
try:
    while True:
        pass
except KeyboardInterrupt:
    print("Stopped listening.")