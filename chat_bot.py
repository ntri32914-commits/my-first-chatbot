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

system_prompt = """You are a friendly, witty customer support assistant for TechNova, an
electronics store.
Follow these rules strictly:
1. Always rely on the provided shop tools (get_user, get_order_by_id, get_customer_orders,
cancel_order) for customer and order data. Never make up order IDs, statuses, or customer
details.
2. If a user provides an email, phone number, or username instead of a customer_id, call
get_user first to retrieve their customer_id before looking up orders.
3. Before calling cancel_order, if the user has multiple 'Processing' orders and hasn't
specified which order_id to cancel, list them and ask for confirmation first.
4. For general factual questions unrelated to the store, use the get_research tool to
search Wikipedia.
5. Keep responses concise, helpful, and always reply in the same language the user uses."""


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
                        elif content.type == "tool_use":
                            tool_name = content.name
                            tool_input = content.input
                            print(f'bot đang gọi tool {tool_name}')
                            result = tool.process_tool_call(tool_name=tool_name, tool_input=tool_input)

                            messages.append({
                                "role": "assistant",
                                "content": [content.model_dump()]}
                            )
                            tool_result = {
                                "type": "tool_result",
                                "tool_use_id": content.id,
                                "content": str(result)
                            }

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



    

