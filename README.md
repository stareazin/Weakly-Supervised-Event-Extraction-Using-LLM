# Weakly-Supervised-Event-Extraction-Using-LLM

## 一、基于提示学习的事件生成方法

**思路借鉴**：[Emancipating Event Extraction from the Constraints of Long-Tailed Distribution Data Utilizing Large Language Models](https://aclanthology.org/2024.lrec-main.501.pdf) COLING 2024 

**数据预处理**：[omnievent](https://github.com/THU-KEG/OmniEvent)，存放在data/processed/ace2005-en

**分解**：data/alpaca.py

**采样-重构-合理性检验**：data/sample.py

**奖励模型打分**：[MoDS](https://github.com/CASIA-LM/MoDS)，保留分数高于-3.5的数据

## 二、基于指令微调的事件抽取方法

**微调框架**：[LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory/tree/main/scripts)

**LoRA**：train/llama3_lora_sft.yaml，参考https://zhuanlan.zhihu.com/p/695287607

**偏好数据**：data/rlhf.py

**DPO**：train/llama3_lora_dpo.yaml，参考https://zhuanlan.zhihu.com/p/705068476

**预测**：

```
bash predict.sh
```

**指标计算**：eval/eval.py

## 三、事件抽取演示系统设计与实现

**系统框架**：[ChatIE](https://github.com/cocacola-lab/ChatIE)

**后端**：tools/back-end 

```
python run.py
```

**前端**：tools/front-end

```
npm install
npm start
```

