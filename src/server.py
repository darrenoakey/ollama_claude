import argparse
import sys
from flask import Flask, request, jsonify
from src import api_handlers
from src.logging_setup import get_logger

logger = get_logger(__name__)

app = Flask(__name__)


# ##################################################################
# route api tags
# handles listing available models endpoint
@app.route("/api/tags", methods=["GET"])
def route_api_tags():
    return jsonify(api_handlers.handle_list_models())


# ##################################################################
# route api chat
# handles chat completion endpoint
@app.route("/api/chat", methods=["POST"])
def route_api_chat():
    data = request.get_json()
    return api_handlers.handle_chat(data)


# ##################################################################
# route api generate
# handles text generation endpoint
@app.route("/api/generate", methods=["POST"])
def route_api_generate():
    data = request.get_json()
    return api_handlers.handle_generate(data)


# ##################################################################
# main
# starts the flask server on specified port
def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=11345)
    parser.add_argument("--host", type=str, default="0.0.0.0")
    args = parser.parse_args(argv)

    logger.info(f"Starting Ollama-Claude proxy on {args.host}:{args.port}")
    print(f"Starting Ollama-Claude proxy on {args.host}:{args.port}")
    print("Logging to output/server.log")
    app.run(host=args.host, port=args.port, debug=False)
    return 0


# ##################################################################
# entry point
# standard python pattern for dispatching main
if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
