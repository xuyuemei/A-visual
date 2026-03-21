import openai  #openai==0.28.1
import time
import socket
import urllib3.exceptions
import requests.exceptions
from openai import OpenAI
# from openai import OpenAI #openai==1.2.0
import requests
import time
api_key = "zk-dcf0b26a7c6965a9e2086e34e6486739"
BASE_URL = "https://api.zhizengzeng.com/v1/"


def ask_gpt(content,model_name,image_base64=None,image_type=None):
    openai.api_key = api_key
    openai.api_base= BASE_URL

    for _ in range(100):
        try:
            # print("Prompt/n",content)
            if image_base64:
                # print("Prompt/n",image_base64)
                response = openai.ChatCompletion.create(
                    model=model_name,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": content},
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:image/{image_type};base64,{image_base64}"}
,}
                            ],
                        }
                    ],
                    temperature=1,
                    request_timeout=60,
                    top_p=0.9,
                    frequency_penalty=0.5,
                    presence_penalty=0.5,
                    # stop=None,
                    max_tokens=4096
                )
            else:
                response = openai.ChatCompletion.create(
                    model=model_name,
                    messages=[
                        {"role": "user", "content": content}
                    ],
                    temperature=1,
                    request_timeout=60,
                    top_p=0.9,
                    frequency_penalty=0.5,
                    presence_penalty=0.5,
                    stop=None,
                    max_tokens=4096
                )
            if 'choices' in response:
                print(response)
                return response.choices[0].message.content
            else:
                print("字典不包含 'choices' 键",response)
                return None

            
        except (socket.timeout, urllib3.exceptions.ReadTimeoutError, requests.exceptions.ReadTimeout,
                openai.error.Timeout, openai.error.ServiceUnavailableError,
                openai.error.RateLimitError, openai.error.APIError):
            # Handle network error and retry
            print("Socket timeout, retrying...")
            time.sleep(30)  # Add a short delay before retrying
    # If max_retries is reached, return an error message
    return "Network error: Max retries reached"

