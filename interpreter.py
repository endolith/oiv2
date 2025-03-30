from litellm import completion
from messages import Message, MessageRole, StreamToken, Response
from typing import List, AsyncGenerator, Optional, Any
from pydantic import BaseModel
from itertools import groupby

class Conversation(BaseModel):
    messages: List[Message] = []
    system_prompt: str = "You are an helpful assistant"
    response_format: Response
    max_recent: int = 5

    def reduce_context(self):
        if len(self.messages) <= self.max_recent:
            return
        
        for message in self.messages[-self.max_recent:]:
            message.content = message.response.summary

    def add_message(self, message: Message):
        self.messages.append(message)
        self.reduce_context()

    def get_messages(self) -> List[Message]:
        response = Response(content=self.system_prompt, summary=self.system_prompt)
        return [Message(role=MessageRole.SYSTEM, response=response, content=response.content)] + self.messages

async def stream_completion(
    messages: List[Message],
    response_format: Response
) -> AsyncGenerator[StreamToken, None]:
    """Stream completion with support for response format"""
    try:
        async for chunk in completion(
            model="openai/local",
            api_key="dummy",
            base_url="http://localhost:1234/v1",
            temperature=0.0,
            messages=[{"role": m.role.value, "content": m.content} for m in messages],
            stream=True
        ):
            if chunk.choices[0].delta.content:
                yield StreamToken(content=chunk.choices[0].delta.content)
        yield StreamToken(content="", done=True)
    except Exception as e:
        yield StreamToken(content="", error=str(e))

async def chat(
    conversation: Conversation,
    prompt: str,
) -> AsyncGenerator[StreamToken, None]:
    """Chat with conversation history"""
    # Add user message
    conversation.add_message(Message(
        role=MessageRole.USER,
        response=Response(content=prompt, summary=""),
        content=prompt
    ))
    
    # Collect assistant's response
    response = ""
    async for token in stream_completion(
        messages=conversation.get_messages(),
        response_format=conversation.response_format
    ):
        if token.error:
            yield token
            return
        if token.content:
            response += token.content
            yield token
        if token.done:
            # Add assistant's complete response to history
            conversation.add_message(Message(
                role=MessageRole.ASSISTANT,
                response=Response(content=response, summary=response),
                content=response
            ))
            yield token

# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def main():
        # Create a conversation with structured response format
        conv = Conversation(response_format=Response(content="", summary=""))
        
        # Chat loop
        while True:
            # Get user input
            user_input = input("\nYou: ").strip()
            if user_input.lower() in ['exit', 'quit']:
                break
                
            # Process the message
            async for token in chat(conv, user_input):
                if token.error:
                    print(f"\nError: {token.error}")
                elif token.content:
                    print(token.content, end="", flush=True)
                if token.done:
                    print("\n")
    
    asyncio.run(main())