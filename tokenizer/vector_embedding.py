from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


text = "Hello, world! this is a test"

response = client.embeddings.create(input=text, model="text-embedding-3-small")

print(
    "vector size: ",
    len(response.data[0].embedding),
    "vector embedding",
    response.data[0].embedding,
)

# positional_embedding = client.embeddings.create(
#     input="positional embedding", model="text-embedding-3-small"
# )

# print(
#     "positional embedding size: ",
#     len(positional_embedding.data[0].embedding),
# )
