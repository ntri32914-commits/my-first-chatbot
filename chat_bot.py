from anthropic import Anthropic
import os
import json
from pathlib import Path
from dotenv import load_dotenv
import tool 


path_env = Path(__file__).resolve().parent /'.env'
path_memory = Path(__file__).resolve().parent/'memory.json'
load_dotenv(dotenv_path=path_env)
client = Anthropic(
    base_url=os.environ['LLM_BASE_URL'],
    api_key=os.environ['LLM_API_KEY']
)
model = os.environ['LLM_MODEL']

system_prompt = '''you are a funny person'''


def reset() -> list[dict] :
    return []

def call_memory() -> list[dict]:
    if path_memory.exists():
        with open(path_memory, mode= 'r', encoding= 'utf-8') as f:
            return json.load(f)
    else: 
        save_memory([])
        with open(path_memory, mode= 'r', encoding= 'utf-8') as f:
            return json.load(f)




def save_memory(messages: list[dict]) -> None:
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
            while True:
                try:
                    resp = client.messages.create(
                        model=model,
                        messages= messages,
                        max_tokens= 4096,
                        system= system_prompt, 
                        tools= tool.TOOLS

                    )
                except Exception as e:
                    print(f'Error calling api {e}')
                    break
                if resp.stop_reason == "tool_use": 
                    for content in resp.content:
                        if content.type == "text":
                            chat = content.text
                            print(f'assistant: {chat}')
                        elif content.type == "tool_use" and content.name  == "get_research":
                            tool_use = content.input

                            messages.append({
                                "role": "assistant",
                                "content": [content.model_dump()]}
                            )
                            tool_result = {
                                "type": "tool_result",
                                "tool_use_id": content.id,
                                "content": 'example' 
                            }

                            topic = tool_use['topic']
                            research = tool.get_research(topic)
                            tool_result['content']= research
                            messages.append({
                                "role": "user",
                                "content": [tool_result]}
                            )
                elif resp.stop_reason == "end_turn":
                    for content in resp.content:
                        if content.type == "text":
                            chat = content.text
                            messages.append(
                                {
                                    'role': 'assistant',
                                    'content': chat
                                }
                            )
                            print(f'assistant: {chat}')
                    break
                else:
                    print(f'stop reason: {resp.stop_reason}')
                    break

             
if __name__ == '__main__':
    call_llm()



    

