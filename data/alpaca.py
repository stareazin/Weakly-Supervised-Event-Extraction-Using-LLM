import json


# 读取原始文件中的数据并进行格式化
def read_examples(input_file):
    examples = []
    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line.strip())
            if "events" in item:
                types, triggers, arguments = [], [], []
                for event in item["events"]:
                    types.append(event["type"])
                    for trigger in event["triggers"]:
                        triggers.append(trigger["trigger_word"])
                        arguments_per_trigger = {
                            arg["role"]: [mention["mention"] for mention in arg["mentions"]]
                            for arg in trigger["arguments"]
                        }
                        arguments.append(arguments_per_trigger)
                example = {"text": item["text"], "type": types, "triggers": triggers, "arguments": arguments}
                if example.get('triggers'):
                    examples.append(example)
    return examples


# 提取特定类型的事件
def get_events_by_type(library, event_type):
    events = []
    for item in library:
        for i in range(len(item["type"])):
            if item["type"][i] == event_type:
                event = {"triggers": item["triggers"][i], "arguments": item["arguments"][i]}
                events.append(event)
    return events


# 提取特定类型的触发词和论元
def merge_by_type(library, event_type):
    triggers = set()
    arguments = {}

    type_events = get_events_by_type(library, event_type)
    for event in type_events:
        triggers.add(event["triggers"])
        for role, mentions in event["arguments"].items():
            if role not in arguments:
                arguments[role] = set()
            for mention in mentions:
                arguments[role].add(mention)

    merged_triggers = list(triggers)
    merged_arguments = {role: list(mentions) for role, mentions in arguments.items()}

    return {
        "type": event_type,
        "triggers": merged_triggers,
        "arguments": merged_arguments
    }


# 构建事件片段库
def json2lib(library):
    event_types = {type for item in library for type in item["type"]}
    merged_result = []
    for event_type in event_types:
        merged_result.append(merge_by_type(library, event_type))
    return merged_result


# 修改字符串的格式
def format(dict):
    string = ""
    formatted_lines = []
    for key, value in dict.items():
        value_str = ", ".join(map(str, value))
        formatted_lines.append(f"{key}: {value_str}")
    string += "; ".join(formatted_lines)
    return string


# 将json数据转换为alpaca格式的数据
def json2alpaca(library):
    tri_data, arg_data = [], []

    for item in library:
        instruction_1 = "Detect event triggers and their corresponding event types from the given text."
        instruction_2 = "Extract event arguments and their roles from the given text based on the detected events."

        input_text = item["text"]
        output_1 = {}
        for key, value in zip(item["type"], item["triggers"]):
            if key in output_1:
                output_1[key].append(value)
            else:
                output_1[key] = [value]
        output_1 = format(output_1)
        tri_data.append({
            "instruction": instruction_1,
            "input": input_text,
            "output": output_1
        })

        for type, trigger, arg in zip(item["type"], item["triggers"], item["arguments"]):
            output_2 = format(arg)
            arg_data.append({
                "instruction": instruction_2,
                "input": input_text,
                "output": output_2,
                "history": [[instruction_1, f"{type}:{trigger}"]]
            })

    return tri_data, arg_data


if __name__ == "__main__":
    library = read_examples('processed/ace2005-en/train.unified.jsonl')

    # merged_result = json2lib(library)
    # with open('event_fragments.json', 'w', encoding='utf-8') as f:
        # json.dump(merged_result, f, ensure_ascii=False, indent=4)

    tri_data, arg_data = json2alpaca(library)
    with open('train/tri_ori_data.json', 'w', encoding='utf-8') as f:
        json.dump(tri_data, f, ensure_ascii=False, indent=4)
    #with open('arg_test_data.json', 'w', encoding='utf-8') as f:
        #json.dump(arg_data, f, ensure_ascii=False, indent=4)
