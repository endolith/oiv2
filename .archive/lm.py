from litellm import completion
import json
import sys
from typing import Dict, Any, List
import threading
import queue
import argparse

def parse_message_content(message: Dict[str, Any]) -> str:
    """Extract text content from a message's versions and content blocks"""
    if "versions" not in message:
        return ""
    
    # Get the currently selected version or the first one
    selected_version = message.get("currentlySelected", 0)
    version = message["versions"][selected_version]
    
    if "content" in version:
        # Handle single step content
        if isinstance(version["content"], list):
            for block in version["content"]:
                if block.get("type") == "text":
                    return block["text"]
    elif "steps" in version:
        # Handle multi-step content
        for step in version["steps"]:
            if step.get("type") == "contentBlock":
                for block in step.get("content", []):
                    if block.get("type") == "text":
                        return block["text"]
    
    return ""

def read_messages(message_queue: queue.Queue, input_file=None):
    """Read messages from stdin (LM Studio output) or from a file"""
    try:
        if input_file:
            # Read from file
            with open(input_file, 'r') as f:
                for line in f:
                    try:
                        message = json.loads(line)
                        if "messages" in message:
                            # Handle conversation messages
                            for msg in message["messages"]:
                                if "role" in msg:
                                    message_queue.put({
                                        "role": msg["role"],
                                        "content": parse_message_content(msg)
                                    })
                        else:
                            # Handle single message
                            message_queue.put(message)
                    except json.JSONDecodeError:
                        continue
        else:
            # Read from stdin
            while True:
                line = sys.stdin.readline()
                if not line:
                    break
                try:
                    message = json.loads(line)
                    if "messages" in message:
                        # Handle conversation messages
                        for msg in message["messages"]:
                            if "role" in msg:
                                message_queue.put({
                                    "role": msg["role"],
                                    "content": parse_message_content(msg)
                                })
                    else:
                        # Handle single message
                        message_queue.put(message)
                except json.JSONDecodeError:
                    continue
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error reading messages: {e}", file=sys.stderr)

def get_user_input(message_queue: queue.Queue):
    """Get user input and add it to the message queue"""
    try:
        while True:
            user_input = input("\nYou: ")
            if user_input.lower() in ['exit', 'quit']:
                break
            message_queue.put({
                "role": "user",
                "content": user_input
            })
    except KeyboardInterrupt:
        pass

def send_to_lmstudio(messages: List[Dict[str, str]], model="openai/local-model", api_base="http://localhost:1234/v1"):
    """Send messages to LM Studio and get response"""
    try:
        response = completion(
            model=model,
            messages=messages,
            api_base=api_base,
            max_tokens=1000,
            temperature=0.0,
            api_key="dummy key",
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return None

def main():
    parser = argparse.ArgumentParser(description='Continue conversation with LM Studio messages')
    parser.add_argument('--file', '-f', help='Path to the LM Studio message file')
    parser.add_argument('--model', '-m', default="openai/local-model", help='Model name (default: openai/local-model)')
    parser.add_argument('--api-base', '-b', default="http://localhost:1234/v1", help='API base URL (default: http://localhost:1234/v1)')
    args = parser.parse_args()

    messages = []
    message_queue = queue.Queue()
    
    # Start threads for reading messages and getting user input
    message_thread = threading.Thread(target=read_messages, args=(message_queue, args.file))
    input_thread = threading.Thread(target=get_user_input, args=(message_queue,))
    
    message_thread.daemon = True
    input_thread.daemon = True
    
    print("Reading messages... (Type 'exit' or 'quit' to end)")
    if args.file:
        print(f"Loading messages from: {args.file}")
    else:
        print("Reading from stdin (pipe LM Studio output)")
    print("You can type your messages below:")
    
    message_thread.start()
    input_thread.start()
    
    try:
        while True:
            try:
                message = message_queue.get(timeout=0.1)
                if "role" in message and "content" in message and message["content"]:
                    messages.append(message)
                    if message["role"] == "user":
                        response = send_to_lmstudio(messages, model=args.model, api_base=args.api_base)
                        if response:
                            print(f"\nAssistant: {response}\n")
                            messages.append({"role": "assistant", "content": response})
            except queue.Empty:
                continue
    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    main()
