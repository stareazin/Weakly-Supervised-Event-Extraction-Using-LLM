import requests
import json
import random
from tqdm import tqdm
from alpaca import json2alpaca
from collections import Counter


# 从事件片段库中采样触发词和论元
def sample_event_data(type, num_arg_types, num_samples):
    with open('event_fragments.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    for event in data:
        if event['type'] == type:
            sampled_trigger = random.choice(event.get("triggers", []))
            arg_types = list(event.get("arguments", {}).keys())
            sampled_arg_types = random.sample(arg_types, min(len(arg_types), num_arg_types))
            sampled_arguments = {
                arg_type: random.sample(event["arguments"][arg_type], min(len(event["arguments"][arg_type]), num_samples))
                for arg_type in sampled_arg_types
            }
            return sampled_trigger, sampled_arg_types, sampled_arguments


# 构造事件生成的提示词
def construct_gen_instruction(type, trigger, roles, arguments):
    '''
    instruction = f'Construct a sentence according to the following requirements: \
    1. It includes certain words: "{trigger}", "{arguments[roles[0]]}", "{arguments[roles[1]]}". Do not include the event type.\
    2. The sentence incorporates an event of type "{type}", where "{trigger}" serves as the trigger for the event, "{arguments[roles[0]]}" plays the role of "{roles[0]}", and "{arguments[roles[1]]}" plays the role of "{roles[1]}". \
    3. The length of the sentence should be within 25 words. Only output the generated sentence without any other content.'
    '''
    instruction = f'Construct a sentence according to the following requirements and rules: \
    Requirements: \
    1. It includes certain words: "{trigger}", "{arguments[roles[0]]}", "{arguments[roles[1]]}". \
    2. The sentence incorporates an event of type "{type}", where "{trigger}" serves as the trigger for the event, "{arguments[roles[0]]}" plays the role of "{roles[0]}", and "{arguments[roles[1]]}" plays the role of "{roles[1]}". \
    Rules: \
    1. Do not include the event type. \
    2. The length of the sentence should be within 25 words. \
    3. Only output the generated sentence without any other content.'
    return instruction


# 构造合理性检验的提示词
def construct_chk_instruction(sentence, type, trigger, roles, arguments):
    instruction = f'Given the sentence "{sentence}", perform the following checks: \
    1. Whether "{trigger}" is the trigger for an event with type "{type}".\
    2. Whether "{arguments[roles[0]]}" plays the role of "{roles[0]}" within the above event.\
    3. Whether "{arguments[roles[1]]}" plays the role of "{roles[1]}" within the above event.\
    If any of the answers to these checks is negative, output "Unreasonable"; otherwise, output "Reasonable". Only output one word.'
    return instruction


# 向API发送请求
def send_request(instruction):
    url = "https://api.siliconflow.cn/v1/chat/completions"
    headers = {
        "Authorization": "Bearer sk-gcjsosddqpqvjmysntvjflbgipzcddgnshusglcrcgwttgdk",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-ai/DeepSeek-V3",
        "messages": [
            {
                "role": "user",
                "content": instruction
            }
        ]
    }
    response = requests.request("POST", url, json=payload, headers=headers)
    try:
        response_data = json.loads(response.text)
        return response_data["choices"][0]["message"]["content"]
    except json.JSONDecodeError:
        return None


# 生成包含新事件的语句并检测合理性
def generate_sentence(type):
    trigger, roles, arguments = sample_event_data(type, 2, 1)
    instruction_gen = construct_gen_instruction(type, trigger, roles, arguments)
    sentence = send_request(instruction_gen)
    instruction_chk = construct_chk_instruction(sentence, type, trigger, roles, arguments)

    if "Unreasonable" in send_request(instruction_chk):
        return
    else:
        return {"text": sentence, "type": [type], "triggers": [trigger], "arguments": [arguments]}


# 统一生成新事件
def generate_events(train_examples, type_count):
    new_tri, new_arg = [], []
    for event_type in type_count.keys():
        filtered_examples = [example for example in train_examples if event_type in example.get('type')]
        if type_count[event_type] >= 200:
            sampled_examples = random.sample(filtered_examples, 200)
        else:
            sampled_examples = filtered_examples
            for i in tqdm(range(200 - type_count[event_type]), desc="Generating sentences"):
                dict = generate_sentence(event_type)
                if dict:
                    sampled_examples.append(dict)
        tri_data, arg_data = json2alpaca(sampled_examples)
        new_tri += tri_data
        new_arg += arg_data
    return new_tri, new_arg


if __name__ == "__main__":
    with open('train_examples.json', 'r', encoding='utf-8') as file:
        train_examples = json.load(file)
    type_count = dict(Counter("".join(item) for example in train_examples for item in example["type"]))

    new_tri, new_arg = generate_events(train_examples, type_count)
    with open('train/tri/tri_new_data.json', 'w', encoding='utf-8') as f:
        json.dump(new_tri, f, ensure_ascii=False, indent=4)
    with open('train/arg/arg_new_data.json', 'w', encoding='utf-8') as f:
        json.dump(new_arg, f, ensure_ascii=False, indent=4)




