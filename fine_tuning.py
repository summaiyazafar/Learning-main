import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client= OpenAI(api_key= os.getenv("OPEN_AI_KEY"))

with open('train.jsonl', 'rb') as f:
    file= client.files.create(
        file= f,
        purpose= 'fine-tune'
    )

print('Uploaded file id:', file.id)

job= client.fine_tuning.jobs.create(
    training_file= file.id,
    model= 'gpt-3.5-turbo'
)

print('Fine_tuning job id:', job.id)