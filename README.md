![](banner.jpg)

# Ollama-Claude Proxy

A proxy server that implements the Ollama API while using Claude as the backend LLM. This allows any Ollama-compatible client to seamlessly use Claude models without code changes.

## Purpose

This proxy enables you to:
- Use Claude models with any application that supports Ollama
- Leverage Claude's capabilities through the familiar Ollama API
- Maintain compatibility with existing Ollama-based workflows and tools
- Access Claude through OpenAI-compatible API endpoints with full JSON schema support

## Installation

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Ensure you have Claude Code authentication configured (the server uses ambient authentication)

## Usage

### Starting the Server

Start the Ollama API server on the default port (11345):
```bash
./run serve
```

Start the OpenAI v1 API server on the default port (11346):
```bash
./run serve-openai
```

Start the Ollama server on a custom port:
```bash
./run serve --port 8080
```

Start the OpenAI server on a custom port (default is base port + 1):
```bash
./run serve-openai --port 8080  # OpenAI server will run on 8081
```

The servers will listen on all network interfaces (0.0.0.0) by default.

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

### Using with OpenAI-Compatible Clients

The server also provides an OpenAI v1 API endpoint with full JSON schema support:

**Using the OpenAI Python library:**
```python
from openai import OpenAI

# Configure client to use the proxy
client = OpenAI(
    base_url="http://localhost:11346/v1",
    api_key="dummy"  # API key not used, but required by the library
)

# Chat completion
response = client.chat.completions.create(
    model="claude",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)

# Chat completion with JSON schema
response = client.chat.completions.create(
    model="claude",
    messages=[{"role": "user", "content": "What is 2+2?"}],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "math_answer",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "answer": {"type": "string"},
                    "confidence": {"type": "number"}
                },
                "required": ["answer", "confidence"],
                "additionalProperties": False
            }
        }
    }
)
print(response.choices[0].message.content)  # Returns valid JSON matching schema
```

**Using curl:**
```bash
# List models
curl http://localhost:11346/v1/models

# Chat completion
curl http://localhost:11346/v1/chat/completions -H "Content-Type: application/json" -d '{
  "model": "claude",
  "messages": [{"role": "user", "content": "Hello!"}]
}'

# Streaming chat
curl http://localhost:11346/v1/chat/completions -H "Content-Type: application/json" -d '{
  "model": "claude",
  "messages": [{"role": "user", "content": "Hello!"}],
  "stream": true
}'

# Chat with JSON schema
curl http://localhost:11346/v1/chat/completions -H "Content-Type: application/json" -d '{
  "model": "claude",
  "messages": [{"role": "user", "content": "What is 2+2?"}],
  "response_format": {
    "type": "json_schema",
    "json_schema": {
      "name": "math_answer",
      "strict": true,
      "schema": {
        "type": "object",
        "properties": {
          "answer": {"type": "string"},
          "confidence": {"type": "number"}
        },
        "required": ["answer", "confidence"],
        "additionalProperties": false
      }
    }
  }
}'
```

## API Endpoints

### Ollama API Endpoints

- `GET /api/tags` - Lists available models (returns "claude")
- `POST /api/chat` - Chat completions with conversation history
- `POST /api/generate` - Single-turn text generation

Both chat and generate endpoints support streaming responses via the `stream` parameter.

### OpenAI v1 API Endpoints

- `GET /v1/models` - Lists available models
- `POST /v1/chat/completions` - Chat completions with full JSON schema support

The OpenAI endpoint supports the `response_format` parameter with JSON schema for structured output. All responses are guaranteed to serialize perfectly into the provided schema.

## Integration Examples

### Continue.dev (VS Code/JetBrains)

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

### Open WebUI

Set the Ollama API URL to `http://localhost:11345` in settings.

### LangChain

```python
from langchain_community.llms import Ollama

llm = Ollama(
    base_url='http://localhost:11345',
    model='claude'
)
response = llm.invoke("What is machine learning?")
```

### LiteLLM

```python
from litellm import completion

response = completion(
    model="openai/claude",
    api_base="http://localhost:11346/v1",
    api_key="dummy",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

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