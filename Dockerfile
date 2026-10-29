FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends build-essential cmake && rm -rf /var/lib/apt/lists/*

# compile llama.cpp for this image: the prebuilt Linux wheel targets musl, not Debian's glibc
RUN CMAKE_ARGS="-DGGML_NATIVE=OFF" pip install --no-cache-dir --no-binary llama-cpp-python llama-cpp-python==0.3.2

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ✏️ the model to deploy (app.py reads these), baked into the image so startup is fast
ENV MODEL_REPO=bartowski/SmolLM2-360M-Instruct-GGUF \
    MODEL_FILE=SmolLM2-360M-Instruct-Q4_K_M.gguf \
    HOST=0.0.0.0
RUN python -c "import os; from huggingface_hub import hf_hub_download; hf_hub_download(os.environ['MODEL_REPO'], os.environ['MODEL_FILE'])"

COPY app.py .
CMD ["python", "app.py"]