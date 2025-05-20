# AI Foundry 多功能 Agent 示例

這個示例展示了如何使用 Azure AI Foundry 框架創建一個多功能 AI 助手，能夠操作檔案系統、PowerPoint 和 Excel 文件。

## 功能

- **檔案系統操作**：瀏覽目錄、讀取/寫入/編輯文件
- **PowerPoint 操作**：創建演示文稿、新增幻燈片、添加文本和圖片
- **Excel 操作**：創建工作簿、讀寫數據、格式化單元格、應用公式 (模擬功能)

## 前置需求

- Python 3.8 或更高版本
- Node.js 和 npm（用於運行 MCP 伺服器）
- Azure OpenAI API 金鑰

## 安裝

1. 安裝 Python 依賴：

```bash
pip install -r requirements.txt
```

2. 安裝所需的 npm 包：

```bash
npm install -g npx
npm install -g @modelcontextprotocol/server-filesystem
npm install -g uvicorn-cli
```

3. 創建 `.env` 文件，添加您的 Azure OpenAI API 憑證：

```
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_API_VERSION=your-api-version
AZURE_OPENAI_ENDPOINT=your-endpoint
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=your-deployment-name
```

## 用法

### 啟動 AI Agent

直接執行以下命令啟動 AI Agent：

```bash
python main_azure_ai_foundry.py
```

檔案系統和 PowerPoint 服務會自動啟動，Excel 功能目前以模擬方式運行。

## 示例指令

以下是一些可以嘗試的指令：

### 檔案系統操作
- "列出 sample_files 目錄中的所有文件"
- "讀取 test.txt 文件的內容"
- "創建一個新文件 hello.txt 並寫入 '你好世界'"

### PowerPoint 操作
- "創建一個新的 PowerPoint 演示文稿"
- "添加一個標題為 '我的演示' 的幻燈片"
- "保存演示文稿到 sample_files/my_presentation.pptx"

### Excel 操作 (模擬功能)
- "創建一個新的 Excel 工作簿"
- "在工作表 Sheet1 的 A1 單元格寫入 '姓名'"
- "保存工作簿到 sample_files/my_workbook.xlsx"

## 注意事項

- Excel 功能目前以模擬方式實現，不會實際創建或修改 Excel 文件
- sample_files 目錄用於存儲由 Agent 創建或修改的文件
- 您可以根據需要修改 `main_azure_ai_foundry.py` 中的 Agent 指令

## 未來擴展

若要實際連接到 Cursor 編輯器中的 excel-stdio 伺服器，需要修改 `ExcelMCPServer` 類，實現真正的 HTTP 通信和工具調用。