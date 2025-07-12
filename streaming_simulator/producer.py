import cv2
import time
import argparse
from kafka import KafkaProducer
import logging

logging.basicConfig(level=logging.INFO)

def video_producer(video_path="video.mp4"):
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda x: x
    )
    
    # Use video file
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        logging.error(f"Cannot open video file: {video_path}")
        return
    
    frame_count = 0
    start_time = time.time()
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            # Serialize frame as JPEG bytes
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            
            # Send to Redpanda topic
            producer.send('video_frames', frame_bytes)
            
            frame_count += 1
            elapsed = time.time() - start_time
            
            if frame_count % 10 == 0:
                fps = frame_count / elapsed
                logging.info(f"Sent {frame_count} frames, FPS: {fps:.2f}")
            
            time.sleep(0.033)  # ~30 FPS
            
    except KeyboardInterrupt:
        logging.info("Producer stopped")
    finally:
        cap.release()
        producer.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Video frame producer for Redpanda')
    parser.add_argument('video_path', help='Path to video file')
    args = parser.parse_args()
    
    video_producer(args.video_path)