![](banner.jpg)

# Ollama-Claude Proxy

A proxy server that implements the Ollama API while using Claude as the backend LLM. This allows any Ollama-compatible client to seamlessly use Claude models without code changes.

## Purpose

This proxy enables you to:
- Use Claude models with any application that supports Ollama
- Leverage Claude's capabilities through the familiar Ollama API
- Maintain compatibility with existing Ollama-based workflows and tools

## Installation

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Ensure you have Claude Code authentication configured (the server uses ambient authentication)

## Usage

### Starting the Server

Start the server on the default port (11345):
```bash
./run serve
```

Start the server on a custom port:
```bash
./run serve --port 8080
```

The server will listen on all network interfaces (0.0.0.0) by default.

### Using with Ollama Clients

Once the server is running, point your Ollama client to the proxy:

**Using the Ollama Python library:**
```python
import ollama

# Configure client to use the proxy
client = ollama.Client(host='http://localhost:11345')

# Chat completion
response = client.chat(model='claude', messages=[
    {'role': 'user', 'content': 'Hello!'}
])
print(response['message']['content'])

# Streaming chat
for chunk in client.chat(model='claude', messages=[
    {'role': 'user', 'content': 'Tell me a story'}
], stream=True):
    print(chunk['message']['content'], end='', flush=True)

# Text generation
response = client.generate(model='claude', prompt='Explain Python decorators')
print(response['response'])
```

**Using curl:**
```bash
# List models
curl http://localhost:11345/api/tags

# Chat completion
curl http://localhost:11345/api/chat -d '{
  "model": "claude",
  "messages": [{"role": "user", "content": "Hello!"}]
}'

# Streaming chat
curl http://localhost:11345/api/chat -d '{
  "model": "claude",
  "messages": [{"role": "user", "content": "Hello!"}],
  "stream": true
}'

# Text generation
curl http://localhost:11345/api/generate -d '{
  "model": "claude",
  "prompt": "Explain recursion"
}'
```

**Using Ollama CLI:**
```bash
# Set the Ollama host
export OLLAMA_HOST=http://localhost:11345

# Run commands as normal
ollama run claude "What is the capital of France?"
```

## API Endpoints

The proxy implements these Ollama API endpoints:

- `GET /api/tags` - Lists available models (returns "claude")
- `POST /api/chat` - Chat completions with conversation history
- `POST /api/generate` - Single-turn text generation

Both chat and generate endpoints support streaming responses via the `stream` parameter.

## Development

### Running Tests

Run a specific test file:
```bash
./run test src/models_test.py
```

Run a specific test function:
```bash
./run test src/models_test.py::test_get_models
```

Run all tests and linting:
```bash
./run check
```

### Linting

Run the linter:
```bash
./run lint
```

### Logs

Server logs are written to `output/server.log` and include detailed request/response information for debugging.

## Examples

### Integration with Existing Tools

Any tool that supports Ollama can use this proxy. For example:

**Continue.dev (VS Code/JetBrains):**
Configure your `config.json` to point to the proxy:
```json
{
  "models": [{
    "title": "Claude via Proxy",
    "provider": "ollama",
    "model": "claude",
    "apiBase": "http://localhost:11345"
  }]
}
```

**Open WebUI:**
Set the Ollama API URL to `http://localhost:11345` in settings.

**LangChain:**
```python
from langchain_community.llms import Ollama

llm = Ollama(
    base_url='http://localhost:11345',
    model='claude'
)
response = llm.invoke("What is machine learning?")
```