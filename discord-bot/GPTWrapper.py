import os
import openai
from dotenv import load_dotenv


load_dotenv()


openai.api_key = os.getenv("OPENAI_API_KEY")

def ask(question, context=None):
    response = openai.Completion.create(
        engine="davinci",
        prompt=f"{context}\nQ: {question}\nA:",
        temperature=0,
        max_tokens=100,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0.3,
        stop=["\n"]
    )
    return response.choices[0].text


if __name__ == '__main__':
    ask("What is the meaning of life?", "The meaning of life is")
