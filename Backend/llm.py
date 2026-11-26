
import json
import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen3:4b"
KEEP_ALIVE = "10m"

# Reuse HTTP connections.
session = requests.Session()


def generate_response(
    prompt,
    temperature=0.2,
    max_tokens=300
):
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "stream": False,
        "think": False,
        "keep_alive": KEEP_ALIVE,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens
        }
    }

    try:
        response = session.post(
            OLLAMA_URL,
            json=payload,
            timeout=(10, 300)
        )
        response.raise_for_status()

        result = response.json()
        return result.get("message", {}).get("content", "").strip()

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Ollama connection failed: {e}")


def generate_response_stream(
    prompt,
    temperature=0.2,
    max_tokens=250
):
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "stream": True,
        "think": False,
        "keep_alive": KEEP_ALIVE,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens
        }
    }

    try:
        with session.post(
            OLLAMA_URL,
            json=payload,
            stream=True,
            timeout=(10, 300)
        ) as response:
            response.raise_for_status()

            for line in response.iter_lines(decode_unicode=True):
                if not line:
                    continue

                data = json.loads(line)

                # Stop if Ollama reports an error.
                if data.get("error"):
                    raise RuntimeError(data["error"])

                token = data.get("message", {}).get("content", "")

                if token:
                    yield token

                if data.get("done"):
                    break

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Ollama connection failed: {e}")
