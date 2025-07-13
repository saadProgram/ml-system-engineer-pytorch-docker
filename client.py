import asyncio
from io import BytesIO

import grpc
from PIL import Image

from inference_service.inference_pb2 import InferenceRequest, InferenceReply
from inference_service.inference_pb2_grpc import InferenceServerStub
import logging
from pprint import pformat
from time import perf_counter

def load_image(image_path):
    """Load image and convert to bytes"""
    image = Image.open(image_path)
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    return buffered.getvalue()

logging.basicConfig(level=logging.INFO)


async def main(image_path):
    image_bytes = load_image(image_path)
    
    async with grpc.aio.insecure_channel("[::]:50052") as channel:
        stub = InferenceServerStub(channel)
        start = perf_counter()

        res: InferenceReply = await stub.inference(
            InferenceRequest(image=[image_bytes, image_bytes, image_bytes])
        )
        logging.info(
            f"[✅] pred = {pformat(res.pred)} in {(perf_counter() - start) * 1000:.2f}ms"
        )


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test gRPC inference client')
    parser.add_argument('image_path', help='Path to test image')
    args = parser.parse_args()
    
    asyncio.run(main(args.image_path))