#  Image Clissification Inference Service

A high-performance PyTorch image classification service with gRPC API, Docker containerization, and Redpanda streaming pipeline. 

## Features

- **PyTorch ResNet34** image classification model
- **gRPC API** for fast inference requests
- **Docker containerization** with multi-stage builds
- **GPU/CPU auto-detection** with fallback support
- **TorchScript optimization** for faster inference
- **Redpanda streaming** for real-time video processing
- **Performance monitoring** with latency and throughput metrics
- **File logging** with timestamps
- **Load testing** capabilities

## Project Structure

```
ml-system-engineer-pytorch-docker/
├── inference_service/
├── streaming_simulator/
├── Images/
├── client.py
├── load_test.py
├── Dockerfile
├── requirements.txt
└── README.md
```

## Quick Start

### 1. Build Docker Image

```bash
docker build -t ml-inference-server .
```

### 2. Start Services

**Terminal 1 - Start Redpanda:**
```bash
docker run -p 9092:9092 redpandadata/redpanda:latest redpanda start --smp 1
```

**Terminal 2 - Start ML Server:**
```bash
docker run --gpus all -p 50052:50052 ml-inference-server
```

### 3. Test the Service

**Simple test:**
```bash
python client.py Images/cat.jpg
```

**Load test:**
```bash
python load_test.py Images/cat.jpg --requests 100 --concurrency 20
```

## Streaming Pipeline

### 1. Create Redpanda Topic
```bash
pip install -r streaming_simulator/requirements.txt
python streaming_simulator/create_topic.py
```

### 2. Start Consumer (Server-side)
```bash
# Run for 60 seconds
python streaming_simulator/consumer.py --duration 60

# Run endlessly
python streaming_simulator/consumer.py
```

### 3. Start Producer (Client-side)
```bash
python streaming_simulator/producer.py path/to/video.mp4
```

## Performance Metrics

The system tracks and logs:
- **Inference latency** per frame (milliseconds)
- **Throughput** (frames per second)
- **Success rate** for requests
- **GPU/CPU utilization**



## Configuration

### Consumer Duration Options
```bash
# Default: endless
python streaming_simulator/consumer.py

# 30 seconds
python streaming_simulator/consumer.py --duration 30

# 120 seconds  
python streaming_simulator/consumer.py --duration 120
```

### Load Test Options
```bash
# Default: 50 requests, 10 concurrent
python load_test.py Images/cat.jpg

# Custom load
python load_test.py Images/cat.jpg --requests 200 --concurrency 50
```

## Docker Configuration

### Health Check
- **Interval**: 60 seconds
- **Timeout**: 10 seconds
- **Retries**: 3

### GPU Support
The Docker image includes CUDA-enabled PyTorch. Run with `--gpus all` to enable GPU acceleration.

## Logging

### Server Logs
- **File**: `logs/inference.log` (inside container)
- **Console**: Real-time output
- **Format**: `YYYY-MM-DD HH:MM:SS,mmm - LEVEL - MESSAGE`

### Accessing Log Files

**Option 1: Mount logs directory to host**
```bash
# Run container with volume mount
docker run --gpus all -p 50052:50052 -v "$(pwd)/logs:/app/logs" ml-inference-server

# View logs on host (in new terminal)
tail -f logs/inference.log
```

**Option 2: Access logs inside container**
```bash
# Get container ID
docker ps

# Access container shell
docker exec -it <container_id> bash

# View logs inside container
tail -f logs/inference.log
```

**Option 3: Copy logs from container**
```bash
# Copy log file to host
docker cp <container_id>:/app/logs/inference.log ./inference.log
```

**Option 4: Use Docker logs (console output only)**
```bash
docker logs -f <container_id>
```

### Consumer Logs
- **Console**: Performance metrics with timestamps
- **Metrics**: Frame count, FPS, latency, predictions

## API Reference

### gRPC Service

**Endpoint**: `localhost:50052`

**Method**: `inference`

**Request**:
```protobuf
message InferenceRequest {
    repeated bytes image = 1;
}
```

**Response**:
```protobuf
message InferenceReply {
    repeated int32 pred = 1;
}
```



## Dependencies

### Core Requirements
- Python 3.12+
- PyTorch (with CUDA support)
- gRPC
- OpenCV
- Pillow

### Streaming Requirements
- kafka-python
- Redpanda (Docker)

## Troubleshooting

### Common Issues

**1. Port already in use**
```bash
docker ps
docker stop <container_id>
```

**2. GPU not detected**
- Ensure NVIDIA Docker runtime is installed
- Run with `--gpus all` flag

**3. Redpanda connection failed**
- Check if Redpanda is running on port 9092
- Verify topic exists: `python streaming_simulator/create_topic.py`

**4. Consumer not processing frames**
- Check if producer sent frames first
- Verify consumer offset: change `auto_offset_reset='earliest'`

### Performance Optimization

1. **Use GPU**: Run with `--gpus all` for 10x speedup
2. **TorchScript**: Already enabled for faster inference
3. **Batch processing**: Send multiple images in single request
4. **Concurrent consumers**: Run multiple consumer instances

## Development

### Generate gRPC Code
```bash
cd inference_service
python -m grpc_tools.protoc --python_out=. --grpc_python_out=. inference.proto
```

### Add New Models
1. Update `inference.py` with new model
2. Rebuild Docker image
3. Test with `load_test.py`


(Followed Medium Blogs)
