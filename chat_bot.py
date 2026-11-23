from openai import OpenAI
import os
import json
from pathlib import Path
from dotenv import load_dotenv


path_env = Path(__file__).resolve().parent /'.env'
path_memory = Path(__file__).resolve().parent/'memory.json'
load_dotenv(dotenv_path=path_env)
client = OpenAI(
    base_url=os.environ['LLM_BASE_URL'],
    api_key=os.environ['LLM_API_KEY']
)
model = os.environ['LLM_MODEL']

system_prompt = '''Bạn là trợ lý vui vẻ, thích kể chuyện cười nhưng không buồn cười
đặc biệt thích chèn từ haha ở mọi câu chat ra vẻ mình vui lắm'''


def reset() -> list[dict[str, str]]:
    return [
        {
            'role': 'system',
            'content': system_prompt
        }
    ]

def call_memory() -> list[dict[str, str]]:
    if path_memory.exists():
        with open(path_memory, mode= 'r', encoding= 'utf-8') as f:
            return json.load(f)
    else: 
        save_memory([
            {
                'role': 'system',
                'content': system_prompt
            }
        ])
        with open(path_memory, mode= 'r', encoding= 'utf-8') as f:
            return json.load(f)




def save_memory(messages: list[dict[str, str]]) -> None:
    with open(path_memory, mode= 'w', encoding='utf-8') as f:
        json.dump(messages, f, indent= 2,ensure_ascii=False)




def call_llm() -> None:
    messages = []

    messages = call_memory()

    while True:
        try:
            req = input('Bạn: ').strip()
        except (KeyboardInterrupt, EOFError) as e:
            print('tạm biệt') 
            break
        if not req:
            continue
        elif req == '/reset':
            messages = reset()
            print('đã reset memory')
        elif req == '/quit':
            print('chào tạm biệt')
            break
        elif req == '/save':
            save_memory(messages)
            print(f'lịch sử chat đã được lưu tại {path_memory.name}')
        else:
            messages.append(
                {
                'role': 'user',
                'content': req
            }
            )
            try:
                resp = client.chat.completions.create(
                    model=model,
                    messages= messages
                )
            except Exception as e:
                print(f'gọi api lỗi {e}')
                continue
            chat = resp.choices[0].message.content
            messages.append(
                {
                    'role': 'assistant',
                    'content': chat
                }
            )
            print(f'assistant: {chat}')
             
if __name__ == '__main__':
    call_llm()



    

