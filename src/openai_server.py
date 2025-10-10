import argparse
import sys
from flask import Flask, request, jsonify
from src import openai_handlers
from src.logging_setup import get_logger

logger = get_logger(__name__)

app = Flask(__name__)


# ##################################################################
# route models
# handles openai list models endpoint
@app.route("/v1/models", methods=["GET"])
def route_models():
    return jsonify(openai_handlers.handle_list_models())


# ##################################################################
# route chat completions
# handles openai chat completions endpoint
@app.route("/v1/chat/completions", methods=["POST"])
def route_chat_completions():
    data = request.get_json()
    return openai_handlers.handle_chat_completions(data)


# ##################################################################
# main
# starts the openai v1 flask server on specified port
def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=11346)
    parser.add_argument("--host", type=str, default="0.0.0.0")
    args = parser.parse_args(argv)

    logger.info(f"Starting OpenAI v1 API server on {args.host}:{args.port}")
    print(f"Starting OpenAI v1 API server on {args.host}:{args.port}")
    print("Logging to output/server.log")
    app.run(host=args.host, port=args.port, debug=False)
    return 0


# ##################################################################
# entry point
# standard python pattern for dispatching main
if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
