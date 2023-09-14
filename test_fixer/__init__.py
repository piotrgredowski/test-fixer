import dotenv
import openai

messages = [{"role": "system", "content": "You are a intelligent assistant."}]


def main():
    openai.api_key = dotenv.get_key(".env", "OPENAI_API_KEY")
    while True:
        message = input("User : ")
        if message:
            messages.append(
                {"role": "user", "content": message},
            )
            chat = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", messages=messages
            )

        reply = chat.choices[0].message.content
        print(f"ChatGPT: {reply}")
        messages.append({"role": "assistant", "content": reply})
