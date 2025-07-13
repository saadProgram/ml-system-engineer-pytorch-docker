# Test script for load gRPC server inference endpoint

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
import grpc
from PIL import Image
from io import BytesIO
import sys
import os

# Add inference_service to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'inference_service'))

from inference_pb2 import InferenceRequest, InferenceReply
from inference_pb2_grpc import InferenceServerStub

# Global variable for image bytes
image_bytes = None

def load_image(image_path):
    """Load image and convert to bytes"""
    global image_bytes
    image = Image.open(image_path)
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    image_bytes = buffered.getvalue()

async def send_request():
    """Send single gRPC request and measure time"""
    try:
        async with grpc.aio.insecure_channel("localhost:50052") as channel:
            stub = InferenceServerStub(channel)
            start = time.perf_counter()
            
            response = await stub.inference(InferenceRequest(image=[image_bytes]))
            
            latency = time.perf_counter() - start
            return latency, True, response.pred
    except Exception as e:
        return 0, False, str(e)

async def load_test(num_requests=50, concurrency=10):
    """Run load test with specified parameters"""
    print(f"Starting load test: {num_requests} requests, {concurrency} concurrent")
    print("=" * 60)
    
    start_time = time.time()
    
    # Create semaphore to limit concurrency
    semaphore = asyncio.Semaphore(concurrency)
    
    async def limited_request():
        async with semaphore:
            return await send_request()
    
    # Send all requests
    tasks = [limited_request() for _ in range(num_requests)]
    results = await asyncio.gather(*tasks)
    
    total_time = time.time() - start_time
    
    # Analyze results
    latencies = [r[0] for r in results if r[1]]
    successes = sum(1 for r in results if r[1])
    failures = num_requests - successes
    
    if latencies:
        # latency in ms
        avg_latency = sum(latencies) / len(latencies) * 1000  
        min_latency = min(latencies) * 1000
        max_latency = max(latencies) * 1000
        throughput = successes / total_time
    else:
        avg_latency = min_latency = max_latency = throughput = 0
    
    # Print results
    print(f"LOAD TEST RESULTS")
    print("=" * 60)
    print(f"Total requests: {num_requests}")
    print(f"Successful: {successes}")
    print(f"Failed: {failures}")
    print(f"Success rate: {(successes/num_requests)*100:.1f}%")
    print(f"Total time: {total_time:.2f}s")
    print(f"Throughput: {throughput:.2f} req/s")
    print(f"Average latency: {avg_latency:.2f}ms")
    print(f"Min latency: {min_latency:.2f}ms")
    print(f"Max latency: {max_latency:.2f}ms")
    print("=" * 60)
    
    if failures > 0:
        print("Some requests failed:")
        for i, (latency, success, result) in enumerate(results):
            if not success:
                print(f"  Request {i+1}: {result}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Load test gRPC inference endpoint')
    parser.add_argument('image_path', help='Path to test image')
    parser.add_argument('--requests', type=int, default=50, help='Number of requests')
    parser.add_argument('--concurrency', type=int, default=10, help='Concurrent requests')
    args = parser.parse_args()
    
    load_image(args.image_path)
    asyncio.run(load_test(args.requests, args.concurrency))