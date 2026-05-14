# WayinBank README

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-brightgreen)](https://modelcontextprotocol.io)

一个专注于金融领域 AI 工具、MCP (Model Context Protocol) 服务与 Python 技能的开源分享仓库。提供开箱即用的金融数据处理、量化分析、API 集成等工具，支持主流 AI Agent 框架无缝接入。

## ✨ 核心特性

- 🛠️ **精选金融 MCP 服务**：行情查询、财报解析、宏观数据、风控指标等标准化接口
- 🧩 **可插拔 Python Skills**：数据清洗、技术指标计算、回测引擎、可视化等模块化技能
- 🤖 **AI Agent 原生支持**：完美兼容 Claude Desktop、ChatGPT、Qwen 等支持 MCP 的 AI 客户端
- 📦 **轻量模块化设计**：按需安装，零配置启动，支持本地/云端部署
- 🔒 **合规优先**：所有数据源均来自公开合规渠道，内置脱敏与频率限制机制

## 📦 快速开始

### 环境要求
- Python 3.10+
- pip / conda 包管理器
- （可选）Docker 用于容器化部署

### 安装依赖
```bash
git clone https://github.com/caifudou/wayinbank.git
cd wayinbank
pip install -r requirements.txt
```

### 配置环境变量
创建 `.env` 文件（参考 `.env.example`）：
```env
FIN_API_KEY=your_api_key_here
DATA_SOURCE=akshare
MCP_PORT=8000
```

## 🚀 使用指南

### 1. 启动 MCP 服务
```bash
python mcp_server/main.py
```

### 2. 在 AI 客户端中接入
以 Claude Desktop 为例，在配置文件中添加：
```json
{
  "mcpServers": {
    "fin-tools": {
      "command": "python",
      "args": ["mcp_server/main.py"],
      "env": {
        "FIN_API_KEY": "your_key"
      }
    }
  }
}
```

### 3. Python Skill 调用示例
```python
from skills.market_data import get_realtime_quote
from skills.indicators import calculate_macd

# 获取实时行情
df = get_realtime_quote(symbol="000001", source="akshare")

# 计算技术指标
df = calculate_macd(df, fast=12, slow=26, signal=9)
print(df.tail())
```

## 📁 项目结构
```
wayinbank/
├── mcp_server/          # MCP 服务核心
│   ├── main.py          # 服务入口
│   └── tools/           # 金融工具集
├── skills/              # Python 技能模块
│   ├── market_data.py   # 行情数据
│   └── indicators.py    # 技术指标
├── examples/            # 使用示例
├── tests/               # 单元测试
├── requirements.txt
└── README.md
```

## 🤝 贡献指南
欢迎提交 Issue 或 Pull Request！请确保：
- 代码遵循 PEP 8 规范
- 新增工具需包含单元测试与文档注释
- 金融数据源需注明出处与使用限制
- 提交前运行 `pytest` 与 `flake8` 检查

## ⚠️ 免责声明
本项目仅供学习与研究使用，不构成任何投资建议。市场有风险，投资需谨慎。所有数据均来自公开渠道，使用者需自行验证数据准确性并遵守相关法律法规。

## 📄 许可证
[MIT License](LICENSE)

## 📬 联系方式
- Issues: [GitHub Issues](https://github.com/caifudou/wayinbank/issues)
- 邮箱: wangliwei@cfdai.com.cn
