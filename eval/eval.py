# 计算微调后模型的评价指标

import json


def parse_arguments(str):
    dict = {}
    args = str.split('; ')
    for arg in args:
        if ':' in arg:
            parts = arg.split(': ', 1)
            if len(parts) >= 2:
                type = parts[0]
                value = parts[1].split(',')
                value = [item.strip() for item in value]
                dict[type] = value
    return dict


def calculate_metrics(type, file_path):
    total_correct, total_predicted, total_actual = 0, 0, 0

    with (open(file_path, 'r', encoding='utf-8') as file):
        for line in file:
            data = json.loads(line)
            predict = parse_arguments(data['predict'])
            label = parse_arguments(data['label'])
            predict_value, label_value = [], []
            for item in predict.values():
                predict_value.extend(item)
            for item in label.values():
                label_value.extend(item)

            if type == 'i':
                total_correct += compare_i(predict_value, label_value)
            elif type == 'c':
                total_correct += compare_c(predict, label)

            total_predicted += len(predict_value)
            total_actual += len(label_value)

    precision = total_correct / total_predicted
    recall = total_correct / total_actual
    f1 = 2 * (precision * recall) / (precision + recall)

    return precision, recall, f1


def compare_i(predict, label):
    return sum(word in label for word in predict)


def compare_c(predict, label):
    correct_count = 0
    for type, values in predict.items():
        if type in label:
            actual_values = label[type]
            for value in values:
                if value in actual_values:
                    correct_count += 1
    return correct_count


if __name__ == "__main__":
    file_path = 'D:/Code/LLaMA-Factory/saves/Qwen2.5-7B/tri/predict/generated_predictions.jsonl'
    # file_path = 'data/origin/arg_ori_result.jsonl'
    type = 'i'

    precision, recall, f1 = calculate_metrics(type, file_path)
    print(f"准确率: {precision * 100:.2f}%, 召回率: {recall * 100:.2f}%, F1: {f1 * 100:.2f}%")


