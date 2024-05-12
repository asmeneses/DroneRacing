from google.cloud import pubsub_v1

def publish_message(project_id: str, topic_id: str, message: str):
    # Initialize Pub/Sub client
    publisher = pubsub_v1.PublisherClient()
    
    # Create the topic path
    topic_path = publisher.topic_path(project_id, topic_id)
    
    # Convert the message to bytes
    message_bytes = message.encode('utf-8')
    
    # Publish the message
    future = publisher.publish(topic_path, data=message_bytes)
    message_id = future.result()
    
    print(f"Message published with ID: {message_id}")