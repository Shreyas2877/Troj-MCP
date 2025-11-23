# Quick Start: Using Troj-MCP with Local Models

This guide will help you set up and use your MCP server with free local models.

## Prerequisites

1. Python 3.11+ installed
2. Virtual environment activated: `source venv/bin/activate`
3. Dependencies installed: `pip install -r requirements.txt`

## Option 1: Using Ollama (Easiest)

### Step 1: Install Ollama

```bash
# macOS
brew install ollama

# Or download from https://ollama.ai
```

### Step 2: Download a Model

```bash
ollama pull llama3
# Or try: ollama pull mistral, ollama pull phi3
```

### Step 3: Run the Client

```bash
python local_model_client.py --model ollama:llama3
```

**Note:** Ollama has limited tool calling support. For full tool calling, use LM Studio or another OpenAI-compatible API.

## Option 2: Using LM Studio (Recommended for Tool Calling)

### Step 1: Install LM Studio

Download from [lmstudio.ai](https://lmstudio.ai) and install.

### Step 2: Setup

1. Open LM Studio
2. Download a model (e.g., Llama 3, Mistral, Phi-3)
3. Go to "Chat" tab
4. Click "Start Server" (runs on port 1234)

### Step 3: Run the Client

```bash
python local_model_client.py --model lmstudio:local --api-base http://localhost:1234/v1
```

## Option 3: Using Continue.dev (VS Code)

### Step 1: Install Continue Extension

1. Open VS Code
2. Install "Continue" extension
3. Restart VS Code

### Step 2: Configure

Create `~/.continue/config.json`:

```json
{
  "models": [
    {
      "title": "Ollama Llama 3",
      "provider": "ollama",
      "model": "llama3",
      "apiBase": "http://localhost:11434"
    }
  ],
  "mcpServers": {
    "troj-mcp": {
      "command": "python",
      "args": ["/Users/trojan/Documents/GitHub/Troj-MCP/main_stdio.py"]
    }
  }
}
```

### Step 3: Use in VS Code

1. Open Continue sidebar
2. Select your model
3. Start chatting - tools are automatically available!

## Troubleshooting

### "MCP server file not found"

Make sure `main_stdio.py` exists in the project directory.

### "Error connecting to MCP server"

1. Check that all dependencies are installed: `pip install -r requirements.txt`
2. Verify Python version: `python --version` (should be 3.11+)
3. Try running the server manually: `python main_stdio.py`

### "Error calling model API"

1. **Ollama**: Make sure Ollama is running: `ollama serve`
2. **LM Studio**: Check that the server is started in the Chat tab
3. Verify the API endpoint is accessible

### Model Not Using Tools

- **Ollama**: Limited tool calling support. Use LM Studio for better results.
- **LM Studio**: Make sure you're using a model that supports function calling (most modern models do)
- Check that tools are listed when the client starts

## Example Usage

Once connected, you can ask:

```
You: What's my system information?
[Model calls get_system_info]
Assistant: Your system is running macOS...

You: Read the README.md file
[Model calls read_file]
Assistant: The README contains...

You: Add 15 and 27
[Model calls add_numbers]
Assistant: 15 + 27 = 42
```

## Next Steps

- See [LOCAL_MODEL_SETUP.md](docs/LOCAL_MODEL_SETUP.md) for detailed documentation
- Explore all available MCP tools
- Customize the system prompt in `local_model_client.py`

