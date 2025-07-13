FROM python:3.12.8-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.12.8-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY inference_service/ ./

EXPOSE 50052
HEALTHCHECK --interval=60s --timeout=10s --retries=3 CMD python -c "import grpc; from inference_pb2_grpc import InferenceServerStub; from inference_pb2 import InferenceRequest; channel=grpc.insecure_channel('localhost:50052'); stub=InferenceServerStub(channel); stub.inference(InferenceRequest(image=[]), timeout=5); channel.close()" || exit 1
CMD ["python", "server.py"]