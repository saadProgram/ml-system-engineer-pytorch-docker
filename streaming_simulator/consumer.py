import asyncio
import time
from io import BytesIO
from kafka import KafkaConsumer
import grpc
import sys
import os

# Add inference_service to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'inference_service'))

from inference_pb2 import InferenceRequest, InferenceReply
from inference_pb2_grpc import InferenceServerStub
import logging
from pprint import pformat

logging.basicConfig(level=logging.INFO)

class PerformanceTracker:
    def __init__(self):
        self.start_time = time.time()
        self.frame_count = 0
        self.total_inference_time = 0
        
    def log_frame(self, inference_time, predictions):
        self.frame_count += 1
        self.total_inference_time += inference_time
        
        elapsed = time.time() - self.start_time
        fps = self.frame_count / elapsed
        avg_latency = self.total_inference_time / self.frame_count * 1000
        
        logging.info(f"Frame {self.frame_count}: {inference_time*1000:.2f}ms | Pred: {predictions} | FPS: {fps:.2f} | Avg latency: {avg_latency:.2f}ms")
        
        # Print summary after 30 seconds
        if elapsed >= 30:
            self.print_summary()
            return True
        return False
    
    def print_summary(self):
        elapsed = time.time() - self.start_time
        avg_fps = self.frame_count / elapsed
        avg_latency = self.total_inference_time / self.frame_count * 1000
        
        print("\n" + "="*50)
        print("30-SECOND PERFORMANCE SUMMARY")
        print("="*50)
        print(f"Total frames processed: {self.frame_count}")
        print(f"Average throughput: {avg_fps:.2f} FPS")
        print(f"Average inference latency: {avg_latency:.2f}ms")
        print(f"Total runtime: {elapsed:.2f}s")
        print("="*50)

async def process_frame(frame_bytes):
    async with grpc.aio.insecure_channel("localhost:50052") as channel:
        stub = InferenceServerStub(channel)
        start = time.perf_counter()
        
        res = await stub.inference(InferenceRequest(image=[frame_bytes]))
        
        inference_time = time.perf_counter() - start
        return res.pred, inference_time

def video_consumer():
    consumer = KafkaConsumer(
        'video_frames',
        bootstrap_servers=['localhost:9092'],
        value_deserializer=lambda x: x,
        auto_offset_reset='earliest'
    )
    
    tracker = PerformanceTracker()
    
    logging.info("Consumer started, waiting for frames...")
    
    try:
        for message in consumer:
            frame_bytes = message.value
            
            # Process frame with inference
            predictions, inference_time = asyncio.run(process_frame(frame_bytes))
            
            # Log performance metrics with predictions
            should_stop = tracker.log_frame(inference_time, predictions)
            
            if should_stop:
                break
                
    except KeyboardInterrupt:
        logging.info("Consumer stopped")
    finally:
        consumer.close()

if __name__ == "__main__":
    video_consumer()