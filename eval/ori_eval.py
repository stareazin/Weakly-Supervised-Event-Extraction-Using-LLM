# 计算未经微调模型的评价指标

import json


def calculate_accuracy(origin_file, test_file):
    with open(origin_file, 'r', encoding='utf-8') as f1:
        origin_data = json.load(f1)
    with open(test_file, 'r', encoding='utf-8') as f2:
        test_data = json.load(f2)

    total_predicted = 0
    total_correct = 0
    total_count = 0

    for origin_item, test_item in zip(origin_data, test_data):
        origin_output = set([word.strip() for word in origin_item.get('output', '').split(',')])
        test_output = set([word.strip() for word in test_item.get('output', '').split(',')])
        total_predicted += len(origin_output)
        total_count += len(test_output)
        for word in test_output:
            if word in origin_output:
                total_correct += 1

    if total_count == 0:
        return 0
    accuracy = total_correct / total_predicted
    recall = total_correct / total_count
    f1 = 2 * (accuracy * recall) / (accuracy + recall)
    return accuracy, recall, f1


if __name__ == "__main__":
    origin_tri_i = 'origin_tri_i.json'
    tri_i_test = 'data/test/tri_i_test.json'
    accuracy, recall, f1 = calculate_accuracy(origin_tri_i, tri_i_test)
    print(f"准确率: {accuracy * 100:.2f}%, 召回率: {recall * 100:.2f}%, F1: {f1 * 100:.2f}%")
