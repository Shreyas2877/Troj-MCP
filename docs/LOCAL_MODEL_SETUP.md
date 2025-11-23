# Using Troj-MCP with Local Models

This guide explains how to use your MCP server with free local models running on your PC instead of Claude Desktop.

## Overview

Instead of using Claude Desktop, you can connect your MCP server to local models like:
- **Ollama** (recommended for beginners)
- **LM Studio** (user-friendly GUI)
- **GPT4All** (lightweight option)
- Any OpenAI-compatible API

## Prerequisites

1. **Python 3.11+** installed
2. **MCP Server** running (this project)
3. **Local Model** installed and running

## Option 1: Using Ollama (Recommended)

### Step 1: Install Ollama

Download and install Ollama from [ollama.ai](https://ollama.ai)

### Step 2: Download a Model

```bash
# Download a model (choose based on your hardware)
ollama pull llama3          # ~4.7GB - Good for most systems
ollama pull llama3:8b       # Smaller version
ollama pull mistral         # Alternative model
ollama pull phi3            # Very lightweight
```

### Step 3: Start Your MCP Server

In one terminal:

```bash
cd /Users/trojan/Documents/GitHub/Troj-MCP && source venv/bin/activate && python main.py
```

The server should start on `http://localhost:8000`

### Step 4: Run the Local Model Client

In another terminal:

```bash
cd /Users/trojan/Documents/GitHub/Troj-MCP && source venv/bin/activate && python local_model_client.py --model ollama:llama3
```

You can now chat with the model, and it will automatically use your MCP tools!

## Option 2: Using LM Studio

### Step 1: Install LM Studio

Download from [lmstudio.ai](https://lmstudio.ai)

### Step 2: Download and Load a Model

1. Open LM Studio
2. Go to "Search" tab
3. Download a model (e.g., Llama 3, Mistral, Phi-3)
4. Go to "Chat" tab
5. Click "Start Server" (usually runs on port 1234)

### Step 3: Start Your MCP Server

```bash
cd /Users/trojan/Documents/GitHub/Troj-MCP
source venv/bin/activate
python main.py
```

### Step 4: Run the Client

```bash
python local_model_client.py --model lmstudio:local --api-base http://localhost:1234/v1
```

## Option 3: Using GPT4All

### Step 1: Install GPT4All

Download from [gpt4all.io](https://gpt4all.io)

### Step 2: Start GPT4All Server

GPT4All typically runs on port 4891. Check the GPT4All documentation for API setup.

### Step 3: Run the Client

```bash
python local_model_client.py --model gpt4all:local --api-base http://localhost:4891/v1
```

## Option 4: Using Continue.dev (VS Code Extension)

Continue.dev is a VS Code extension that supports both local models and MCP servers.

### Step 1: Install Continue.dev

1. Open VS Code
2. Install the "Continue" extension
3. Restart VS Code

### Step 2: Configure Continue

Create or edit `~/.continue/config.json`:

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

1. Open Continue sidebar in VS Code
2. Select your local model
3. Start chatting - MCP tools will be available automatically!

## Option 5: Custom OpenAI-Compatible API

If you have any other OpenAI-compatible API running locally:

```bash
python local_model_client.py \
  --model openai:your-model-name \
  --api-base http://localhost:YOUR_PORT/v1
```

## Troubleshooting

### MCP Server Not Starting

```bash
# Check if port 8000 is already in use
lsof -i :8000

# Kill the process if needed
kill -9 <PID>

# Try a different port
export SERVER_PORT=8001
python main.py
```

### Model Not Responding

1. **Ollama**: Make sure Ollama is running
   ```bash
   ollama serve
   ```

2. **LM Studio**: Check that the server is started in the Chat tab

3. **Check API endpoint**: Test with curl
   ```bash
   curl http://localhost:11434/api/tags  # Ollama
   curl http://localhost:1234/v1/models   # LM Studio
   ```

### Tools Not Working

1. Make sure MCP server is running and accessible
2. Check the MCP server logs for errors
3. Verify the tool names match between client and server

## Advanced Usage

### Running MCP Server in Background

```bash
# Using nohup
nohup python main.py > mcp.log 2>&1 &

# Using screen
screen -S mcp-server
python main.py
# Press Ctrl+A then D to detach
```

### Custom Model Configuration

Edit `local_model_client.py` to customize:
- Tool calling behavior
- System prompts
- Temperature settings
- Model parameters

### Using with Multiple Models

You can run multiple instances with different models:

```bash
# Terminal 1: Ollama
python local_model_client.py --model ollama:llama3

# Terminal 2: LM Studio
python local_model_client.py --model lmstudio:local --api-base http://localhost:1234/v1
```

## Performance Tips

1. **Choose the right model size** for your hardware:
   - 4-8GB RAM: Use 3B-7B parameter models
   - 8-16GB RAM: Use 7B-13B parameter models
   - 16GB+ RAM: Can handle larger models

2. **Use quantization**: Most local model tools support quantized models (Q4, Q5) which are smaller and faster

3. **GPU acceleration**: If you have a compatible GPU, models will run much faster

## Example Interactions

Once connected, you can ask the model to:

```
You: What's my system information?
[Model calls get_system_info tool]
Assistant: Your system is running macOS 25.0.0...

You: Read the file README.md
[Model calls read_file tool]
Assistant: The README contains...

You: Add 15 and 27
[Model calls add_numbers tool]
Assistant: 15 + 27 = 42
```

## Next Steps

- Explore all available MCP tools
- Customize the system prompt in `local_model_client.py`
- Integrate with other local model tools
- Set up automated workflows

## Support

If you encounter issues:
1. Check the logs in `main.log` or `mcp.log`
2. Verify all services are running
3. Check network connectivity
4. Review the troubleshooting section above

