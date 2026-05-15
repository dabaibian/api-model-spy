# 🔍 api-model-spy

<div align="center">

**English** | [中文](#中文说明)

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![OpenAI Compatible](https://img.shields.io/badge/API-OpenAI%20Compatible-412991.svg)]()
[![Anthropic](https://img.shields.io/badge/API-Anthropic-orange.svg)]()

> Detect API model dilution and fingerprint which LLM is **actually** running behind any endpoint.

</div>

---

## What is this?

Many third-party LLM API providers claim to serve premium models (GPT-4, Claude Opus, etc.) but quietly substitute cheaper models to cut costs — a practice known as **"model dilution"** (掺水).

`api-model-spy` helps you find out what's really running by sending a battery of diagnostic probes and comparing the responses against a database of known model signatures.

## Features

- 🕵️ **Fingerprint any API** — 10 diagnostic probes covering identity, reasoning, tokenization, and latency
- 🚨 **Detect dilution** — flags when the detected model is a lower tier than what was claimed
- 💰 **Price anomaly check** — automatically warns when pricing is implausibly cheap
- 🧠 **16+ model signatures** — GPT-3.5/4/4o/o1, Claude 3/3.5/4, Gemini, Llama, Mistral
- 🔌 **Dual API support** — OpenAI-compatible endpoints and Anthropic API

## Quick Start

```bash
# Step 1: Run fingerprinting probes against the target API
python3 scripts/probe.py \
  --api-type openai \
  --api-key YOUR_KEY \
  --model gpt-4-turbo \
  --endpoint https://api.third-party.com/v1 \
  --claimed-model "GPT-4 Turbo" \
  --output probe_results.json

# Step 2: Analyze the results
python3 scripts/analyze.py probe_results.json \
  --claimed-model "GPT-4 Turbo" \
  --output report.txt

cat report.txt
```

**Dependencies** (auto-installed by probe.py):
```bash
pip install openai anthropic requests
```

Python 3.9+ required.

## Example Output

```
============================================================
  API MODEL DETECTOR -- ANALYSIS REPORT
============================================================
  Model param used: gpt-4-turbo
  Claimed model   : GPT-4 Turbo

  !! DILUTION ALERT
     Claimed : GPT-4 Turbo (premium tier)
     Detected: GPT-3.5 Turbo (budget tier)
     Tier drop: 2 level(s) -- possible model substitution

  DETECTED MODEL : GPT-3.5 Turbo
  Provider       : OpenAI
  Confidence     : HIGH (40 pts)

  OBSERVATIONS
  Self-identity  : i'm gpt-3.5, a language model developed by openai
  Knowledge cutoff: 2021-09  (expected 2023-12 for GPT-4 Turbo)
  Strawberry test: FAIL
  Decimal test   : FAIL
  Avg latency    : 212 ms

  TOP CANDIDATES
  #1  GPT-3.5 Turbo    score=40  tier=budget
  #2  GPT-4o Mini      score=17  tier=budget
  #3  GPT-4o           score=12  tier=mid
============================================================
```

## How It Works

The tool sends 10 carefully designed probe prompts that elicit model-specific behaviors:

| Probe | What it detects |
|---|---|
| Self-identification | Model identity (if not suppressed by provider) |
| Knowledge cutoff | Training data recency — different models have different cutoff dates |
| Strawberry letter count | Tokenization quirks (GPT-3.5 often answers "2" instead of "3") |
| 9.11 vs 9.9 comparison | Basic numerical reasoning (older models frequently fail this) |
| Multi-step math | Arithmetic reasoning quality |
| Logic puzzle | Deduction capability |
| Response latency | Model size proxy (large models are slower) |
| `reasoning_tokens` in usage | Identifies o1/o3-class models — their unique fingerprint |

## Real-World Test: xdai.pro "gpt-5.5"

We tested a provider selling a model called `gpt-5.5` (a non-existent OpenAI version):

- **`reasoning_tokens` present** in every response → only o1/o3 class models produce this
- **Knowledge cutoff:** June 2024 → matches o1 series
- **Latency:** 4–10 seconds → consistent with o1-mini's thinking phase
- **Verdict:** `gpt-5.5` is likely **o1-mini** with a fake marketing name

## Supported Models

| Provider | Models |
|---|---|
| OpenAI | GPT-3.5 Turbo, GPT-4, GPT-4 Turbo, GPT-4o, GPT-4o Mini, o1 |
| Anthropic | Claude 3 Haiku/Sonnet/Opus, Claude 3.5 Sonnet/Haiku, Claude Sonnet 4, Claude Opus 4 |
| Google | Gemini 1.5 Pro, Gemini 1.5 Flash |
| Meta | Llama 3 70B |
| Mistral AI | Mistral Large |

## File Structure

```
api-model-spy/
├── scripts/
│   ├── probe.py          # Sends fingerprinting probes to the target API
│   └── analyze.py        # Analyzes responses and generates report
└── references/
    └── model_signatures.md   # Known model characteristics database
```

## License

MIT © [dabaibian](https://github.com/dabaibian)

---

<div align="center" id="中文说明">

**[English](#-api-model-spy)** | 中文

</div>

## 🔍 api-model-spy — 中文说明

> 检测 API 掺水行为，反向推理任何 LLM 接口背后实际运行的是哪个模型。

---

## 这是什么？

很多第三方 LLM API 服务商声称提供高端模型（GPT-4、Claude Opus 等），实际上悄悄替换成更便宜的模型来降低成本，这种行为俗称**"掺水"**。

`api-model-spy` 通过向目标接口发送一组精心设计的"指纹探针"，并将响应与已知模型特征库对比，帮你找出实际运行的是什么模型。

## 功能特点

- 🕵️ **指纹识别任意 API** — 10 条诊断探针，覆盖身份、推理、分词特征和延迟
- 🚨 **掺水检测** — 当检测到的模型档次低于声称模型时自动报警
- 💰 **价格异常预警** — 遇到不合理的低价自动提示（如声称 Opus 却只收 $0.50/M）
- 🧠 **16+ 模型特征库** — GPT-3.5/4/4o/o1、Claude 3/3.5/4、Gemini、Llama、Mistral
- 🔌 **双接口支持** — 兼容 OpenAI 格式接口和 Anthropic 原生接口

## 快速开始

```bash
# 第一步：向目标 API 发送指纹探针
python3 scripts/probe.py \
  --api-type openai \
  --api-key 你的密钥 \
  --model gpt-4-turbo \
  --endpoint https://第三方服务商地址/v1 \
  --claimed-model "GPT-4 Turbo" \
  --output probe_results.json

# 第二步：分析结果
python3 scripts/analyze.py probe_results.json \
  --claimed-model "GPT-4 Turbo" \
  --output report.txt

cat report.txt
```

**依赖安装**（probe.py 会自动安装）：
```bash
pip install openai anthropic requests
```

需要 Python 3.9 及以上版本。

## 工作原理

工具向目标接口发送 10 条特殊设计的探针问题，利用不同模型在以下方面的行为差异来识别身份：

| 探针 | 检测内容 |
|---|---|
| 身份自述 | 模型是否会透露自己的名称 |
| 知识截止日期 | 训练数据的时间范围（不同模型差异明显） |
| Strawberry 字母计数 | 分词特征（GPT-3.5 常答"2 个 r"而不是正确的"3 个"） |
| 9.11 vs 9.9 比较 | 基础数值推理能力（旧模型常答错） |
| 多步骤数学题 | 算术推理质量 |
| 逻辑谜题 | 演绎推理能力 |
| 响应延迟 | 模型规模的间接指标（大模型更慢） |
| `reasoning_tokens` 字段 | o1/o3 系列模型的专属指纹 |

## 真实案例：xdai.pro 的 "gpt-5.5"

我们对一家售卖 `gpt-5.5` 模型的服务商进行了测试（OpenAI 从未发布该版本）：

- **每次响应均包含 `reasoning_tokens`** → 这是 o1/o3 系列的专属特征
- **知识截止日期：2024 年 6 月** → 与 o1 系列吻合
- **响应延迟：4–10 秒** → 符合 o1-mini 的"思考阶段"特征
- **结论：`gpt-5.5` 极大概率是披着假名字的 o1-mini**

## 检测报告示例

```
============================================================
  API MODEL DETECTOR -- ANALYSIS REPORT
============================================================
  使用的 Model 参数: gpt-4-turbo
  声称的模型      : GPT-4 Turbo

  !! 掺水警告
     声称: GPT-4 Turbo（高端档）
     检测: GPT-3.5 Turbo（经济档）
     档次差: 2 级 — 疑似模型替换

  检测结果: GPT-3.5 Turbo
  置信度  : 高 (40 分)

  观测信号:
  自我报告  : 我是 GPT-3.5，OpenAI 开发的语言模型
  知识截止  : 2021-09（GPT-4 Turbo 应为 2023-12）
  Strawberry: 答错
  延迟      : 212ms（远低于 GPT-4 Turbo 正常水平）
============================================================
```

## 支持的模型

| 服务商 | 模型 |
|---|---|
| OpenAI | GPT-3.5 Turbo、GPT-4、GPT-4 Turbo、GPT-4o、GPT-4o Mini、o1 |
| Anthropic | Claude 3 Haiku/Sonnet/Opus、Claude 3.5 Sonnet/Haiku、Claude Sonnet 4、Claude Opus 4 |
| Google | Gemini 1.5 Pro、Gemini 1.5 Flash |
| Meta | Llama 3 70B |
| Mistral AI | Mistral Large |

## 文件结构

```
api-model-spy/
├── scripts/
│   ├── probe.py          # 向目标 API 发送指纹探针
│   └── analyze.py        # 分析响应并生成报告
└── references/
    └── model_signatures.md   # 已知模型特征库
```

## 开源协议

MIT © [dabaibian](https://github.com/dabaibian)
