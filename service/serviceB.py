# Use a pipeline as a high-level helper
from transformers import pipeline

pipe = pipeline("text-generation", model="microsoft/bitnet-b1.58-2B-4T", trust_remote_code=True)
messages = [
    {"role": "user", "content": "Who are you?"},
]
pipe(messages)