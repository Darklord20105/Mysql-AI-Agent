import os
import requests


LLM_BASE_URL = os.getenv(
    "LLM_BASE_URL",
    "http://127.0.0.1:11434"
)

LLM_MODEL = os.getenv(
    "LLM_MODEL",
    "qwen2.5:3b"
)

LLM_TIMEOUT = int(
    os.getenv("LLM_TIMEOUT", "180")
)


def generate_response(
    prompt,
    system_prompt=None,
    model=None,
    output_format=None
):

    url = f"{LLM_BASE_URL}/api/chat"

    messages = []

    if system_prompt:
        messages.append({
            "role": "system",
            "content": system_prompt
        })

    messages.append({
        "role": "user",
        "content": prompt
    })

    payload = {
        "model": model or LLM_MODEL,
        "messages": messages,
        "stream": False
    }

    # Request structured JSON when needed.

    if output_format:
        payload["format"] = output_format

    try:

        response = requests.post(
            url,
            json=payload,
            timeout=LLM_TIMEOUT
        )

        response.raise_for_status()

        result = response.json()

        return result["message"]["content"]

    except requests.exceptions.ConnectionError:

        raise RuntimeError(
            "Could not connect to Ollama. "
            "Make sure the Ollama container is running."
        )

    except requests.exceptions.Timeout:

        raise RuntimeError(
            "Ollama request timed out."
        )

    except requests.exceptions.HTTPError as error:

        raise RuntimeError(
            f"Ollama returned an HTTP error: {error}"
        )

    except (KeyError, ValueError) as error:

        raise RuntimeError(
            f"Invalid response received from Ollama: {error}"
        )