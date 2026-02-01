# Wazuh AI Security Agent

一个基于 AI 驱动的安全运营助理，集成 Wazuh SIEM 平台与 DeepSeek 大模型。通过自然语言对话，实现自动化的安全监控、漏洞查询与资产管理。

![界面预览](docs/preview.png)

## ✨ 核心功能

*   **🛡️ 智能对话界面**：提供暗色主题的现代化 Web UI，支持流式对话体验。
*   **🧠 DeepSeek 集成**：内置 DeepSeek R1/V3 模型支持，能够理解复杂的安全指令。
*   **🔍 自动化 Wazuh 操作**：
    *   **Agent 管理**：查询在线终端、系统信息、健康状态。
    *   **漏洞扫描**：自动检索 Agent 存在的 CVE 漏洞及严重程度。
    *   **告警分析**：实时获取并分析高危安全告警。
*   **🔌 零侵入部署**：通过 API 与现有的 Wazuh 环境连接，无需在 Agent 端安装额外插件。

## 🛠️ 系统架构

*   **Frontend**: HTML5 + TailwindCSS (响应式设计)
*   **Backend**: Python FastAPI (异步高性能)
*   **LLM Engine**: DeepSeek API (推理与工具调用)
*   **Security Platform**: Wazuh Manager & Indexer API

## 🚀 快速开始

### 前置要求

*   Python 3.8+
*   Wazuh Server (v4.8+)
*   DeepSeek API Key

### 1. 配置环境

在项目根目录创建 `.env` 文件（或修改现有的）：

# Wazuh Manager 配置
WAZUH_HOST=192.168.xx.xx
WAZUH_PORT=55000
WAZUH_USER=wazuh
WAZUH_PASS=您的WazuhAPI密码
WAZUH_VERIFY_SSL=false

# Wazuh Indexer 配置 (用于漏洞查询)
WAZUH_INDEXER_HOST=192.168.xx.xx
WAZUH_INDEXER_PORT=9201
WAZUH_INDEXER_USER=admin
WAZUH_INDEXER_PASSWORD=您的Indexer密码
