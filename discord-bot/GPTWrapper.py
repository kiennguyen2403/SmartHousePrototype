import os
import openai
from dotenv import load_dotenv


load_dotenv()


openai.api_key = os.getenv("OPENAI_API_KEY")

def ask(question, context=None):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"You are a smart house assistant. {context}"},
            {"role":"user","content":f"{question}"}
        ]

    )
    # print(response)
    return response.choices[0].message.content


if __name__ == '__main__':
    print(ask("how to make a "))
