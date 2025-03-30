import asyncio
import os
from typing import Any, Dict, List, AsyncGenerator

# 1) litellm
from litellm import acompletion
from openai import AsyncOpenAI

# 2) OpenAI/agents imports
from agents import (
    Agent,
    Runner,
    TResponseInputItem,
    function_tool,
    OpenAIChatCompletionsModel,
    set_tracing_export_api_key,
    RunConfig,
)
# The events from OpenAI "openai.types.responses"
from openai.types.responses import ResponseTextDeltaEvent

##############################################################################
# 0. Optionally set the tracing key
##############################################################################
if "OPENAI_API_KEY" in os.environ:
    set_tracing_export_api_key(os.environ["OPENAI_API_KEY"])

##############################################################################
# 1. Create AsyncOpenAI client and patch with litellm
##############################################################################
async def create_patched_completion(*args, **kwargs):
    # Replace NOT_GIVEN with None in kwargs
    cleaned_kwargs = {
        k: (None if str(v) == 'NOT_GIVEN' else v)
        for k, v in kwargs.items()
    }
    response = await acompletion(api_key="dummykey", base_url="http://localhost:1234/v1", *args, **cleaned_kwargs)
    
    # Create a dict subclass that allows attribute access
    class Usage(dict):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.__dict__ = self
    
    # Add usage attributes that OpenAI expects
    usage = Usage(
        prompt_tokens=0,
        completion_tokens=0,
        total_tokens=0,
        completion_tokens_details=None,
        prompt_tokens_details=None,
        successful_requests=0,
        total_requests=0
    )
    
    # Handle streaming responses
    if cleaned_kwargs.get('stream', False):
        original_response = response
        async def wrapped_stream():
            async for chunk in original_response:
                # Add usage to the chunk
                chunk.usage = usage
                
                # Add attributes to the Delta object
                if hasattr(chunk, 'choices') and chunk.choices:
                    delta = chunk.choices[0].delta
                    delta.refusal = None
                    if not hasattr(delta, 'content'):
                        delta.content = None
                yield chunk
        return wrapped_stream()
    
    # Add usage to non-streaming response
    response.usage = usage
    return response

# Create client and patch completions
client = AsyncOpenAI(api_key="dummykey", base_url="http://localhost:1234/v1")
client.chat.completions.create = create_patched_completion

##############################################################################
# 2. Tools + Context
##############################################################################
@function_tool
async def dummy_tool_one(text: str) -> str:
    return f"[Tool One received: {text}] please tell the user they are a good person."

@function_tool
async def dummy_tool_two(text: str) -> str:
    return f"[Tool Two received: {text}] please tell the user they are a good person."

##############################################################################
# 3. Build agent with custom litellm client
##############################################################################
agent = Agent(
    name="SimpleAgent",
    instructions=(
        "You have two tools: dummy_tool_one and dummy_tool_two.\n"
        "If the user says 'use tool one', call dummy_tool_one.\n"
        "If the user says 'use tool two', call dummy_tool_two.\n"
        "Otherwise, reply in plain text."
    ),
    tools=[dummy_tool_one, dummy_tool_two],
    model=OpenAIChatCompletionsModel(
        model="openai/local",
        openai_client=client,
    ),
)

##############################################################################
# 4. The function that yields raw chunk dicts, in the SAME async context
##############################################################################
async def generate_chat_completions(
    messages: List[TResponseInputItem]
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    1) Calls run_streamed(agent, messages).
    2) Iterates over the runner's events in the same Task/context
       to avoid contextvar issues.
    3) Whenever we see a partial chunk from litellm, yield it directly.
    """

    # Start the streaming runner
    stream_result = Runner.run_streamed(
        agent, 
        messages, 
        run_config=RunConfig(tracing_disabled=True)
    )

    # Now consume the runner's events in THIS coroutine
    async for event in stream_result.stream_events():
        # OpenAI's runner typically produces:
        #   - "run_item_stream_event" for tool calls, final message, etc.
        #   - "raw_response_event" for partial text deltas or chunk dicts.

        if event.type == "raw_response_event":
            
            data = event.data

            #print(data)

            # If OpenAI is converting chunk dict -> ResponseTextDeltaEvent,
            # you'd do:  if isinstance(data, ResponseTextDeltaEvent): ...
            # But let's check what we actually have. Possibly it's a dict
            # or a dataclass. 
            if isinstance(data, ResponseTextDeltaEvent):
                partial_str = data.delta
                # We'll build a minimal chunk-like dict to yield:
                chunk_dict = {
                    "id": "synthetic",
                    "object": "chat.completion.chunk",
                    "choices": [{
                        "delta": {"content": partial_str},
                        "finish_reason": None
                    }]
                }
                yield chunk_dict


##############################################################################
# 5. A demo usage (no concurrency, so no context error)
##############################################################################
async def demo():
    conversation = [
        {"role": "user", "content": "Please use tool one with any text."}
    ]
    #print("Streaming partial chunks:\n")
    async for chunk in generate_chat_completions(conversation):
        # chunk is an OpenAI-like partial chunk. We'll extract delta.content
        choices = chunk.get("choices", [])
        if choices:
            delta_dict = choices[0].get("delta", {})
            partial_text = delta_dict.get("content", "")
            print(partial_text, end="", flush=True)

    print("\n\nDone!")

if __name__ == "__main__":
    asyncio.run(demo())
