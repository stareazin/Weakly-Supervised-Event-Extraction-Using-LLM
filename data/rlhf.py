# 利用模型的预测结果生成偏好数据

import json
from eval import parse_arguments


def json2shgpt(input_file, output_file):
    transformed_data = []
    special_symbols = ["<|begin_of_text|>", "<|eot_id|>", "<|start_header_id|>assistant<|end_header_id|>", "<|start_header_id|>user<|end_header_id|>", "\n"]

    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line)
            prompt, predict, label = data['prompt'], data['predict'], data['label']
            for symbol in special_symbols:
                prompt = prompt.replace(symbol, "")

            if parse_arguments(predict) != parse_arguments(label):
                new_data = {
                    "conversations": [
                        {
                            "from": "human",
                            "value": prompt
                        }
                    ],
                    "chosen": {
                        "from": "gpt",
                        "value": label
                    },
                    "rejected": {
                        "from": "gpt",
                        "value": predict
                    }
                }
                transformed_data.append(new_data)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(transformed_data, f, ensure_ascii=False, indent=2)
    print(f"Sharegpt format data has been saved to {output_file}")


if __name__ == "__main__":
    input_file = 'D:/Code/LLaMA-Factory/saves/LLaMA3-8B/lora/arg/high_quality_arg/3.26/predict/generated_predictions.jsonl'
    output_file = 'data/train/arg_high_rlhf.json'
    json2shgpt(input_file, output_file)