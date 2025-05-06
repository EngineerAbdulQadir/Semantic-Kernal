# Multi Agent System With MCP Server

A simple two‑part setup:

1. **`mcp_server.py`**  
   A JSON‑RPC tool server (providing `lookup_wikipedia`) built with FastMCP.

2. **`main.py`**  
   A Semantic Kernel client that:
   - Calls the MCP tool to fetch a definition.
   - Chains three Gemini‑powered agents (research, writing, polishing).
   - Writes its output to `output.md`.

---

## 🚀 Prerequisites

- **Python** ≥ 3.12  
- **UV Python Package Installer**  

---

## 📦 Install Dependencies

```bash
uv add python-dotenv semantic-kernel "mcp[cli]"
````

---

## 🔧 Configuration

Create a file named `.env` in the project root:

```dotenv
GEMINI_API_KEY=your_gemini_api_key_here
```

---

## 🏃‍♂️ Running the MCP Server

In one terminal, run:

```bash
mcp run mcp_server.py
```

---

## 🏃‍♀️ Running the Client

In another terminal, run:

```bash
uv run main.py "The future of AI in healthcare"
```

---

## 📁 Project Structure

```
.venv
__pycache__
.env
.gitignore
.python-version
main.py
mcp_server.py
output.md
pyproject.toml
Readme.md
uv.lock
```

---

## 📝 License

MIT © EngineerAbdulQadir

---