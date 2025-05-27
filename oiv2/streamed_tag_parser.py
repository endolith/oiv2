import re
from typing import List, Optional

class StreamTaggedResponse:
    """Incremental parser for assistant XML‑style tags.

    Args:
        tool_tag_prefix (str): Base name for tool tags (default "tool").
    """

    REASONING_TAGS = {"think", "thinking", "reasoning"}

    def __init__(self):
        self.state = "outside"
        self.current_tag: Optional[str] = None
        self.buffer_tag = ""
        self.buffer_text = ""
        self.message_out = ""
        self.reasoning_out = ""
        self.tool_names: List[str] = []
        self.tool_args: List[str] = []

    # Properties -----------------------------------------------------------
    @property
    def message(self):
        return self.message_out

    @property
    def reasoning(self):
        return self.reasoning_out

    @property
    def tool_calls(self):
        return [
            {"name": n, "args": a}
            for n, a in zip(self.tool_names, self.tool_args)
        ]

    # Internal helpers -----------------------------------------------------
    def _flush_buffer_text(self):
        if self.current_tag is None:
            # outside any tag → message
            self.message_out += self.buffer_text
        elif self.current_tag in self.REASONING_TAGS:
            self.reasoning_out += self.buffer_text
        elif self.current_tag == "tool_name":
            self.tool_names.append(self.buffer_text.strip())
        elif self.current_tag == "tool_args":
            self.tool_args.append(self.buffer_text.strip())
        elif self.current_tag == "message":
            self.message_out += self.buffer_text
        # else unknown tag – ignore for now
        self.buffer_text = ""

    # Public feed ----------------------------------------------------------
    def feed(self, chunk: str) -> str:
        """Feed a token/substring and return *new* printable message text."""
        printable = ""
        for ch in chunk:
            if self.state == "outside":
                if ch == "<":
                    self._flush_buffer_text()
                    self.state = "tag_open"
                    self.buffer_tag = "<"
                else:
                    # accumulate outside text directly to message_out & printable
                    self.message_out += ch
                    printable += ch
            elif self.state == "tag_open":
                self.buffer_tag += ch
                if ch == ">":
                    tag = self.buffer_tag
                    self.buffer_tag = ""
                    # Determine if opening or closing
                    is_close = tag.startswith("</")
                    tag_name = re.sub(r"[</> ]", "", tag)
                    if is_close:
                        self._flush_buffer_text()
                        self.current_tag = None
                    else:
                        # opening tag
                        self.current_tag = tag_name
                    self.state = "outside"  # resume scanning text
            else:
                # Should not reach here; fallback
                self.state = "outside"
        return printable