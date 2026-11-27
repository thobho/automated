"""Image parts in AI messages (US-11.3B, D59).

A message `content` is normally a string. A caller that passes `allow_images=True` to
`complete()` may instead give a list of parts:

    {"type": "text", "text": "..."}            # scrubbed like any text
    {"type": "image", "data": <PNG/JPEG bytes>}

Checked before anything is sent: the type is sniffed from the bytes (never trusted from a name or
a claimed media type), each image and the number of images are limited, and every image is counted
in the cost plan at `IMAGE_TOKENS_ESTIMATE` tokens. Images are never logged and never stored
(`AICall` keeps no prompt). Which pictures may be sent is the caller's duty: in the MVP only
screenshots of `synthetic` packages (see `apps.quality.screenshots`).
"""

import base64

from .errors import AIError

MAX_IMAGE_BYTES = 3_000_000  # per image
MAX_IMAGES_PER_CALL = 4
MAX_PARTS_PER_MESSAGE = 16
# Upper estimate of the prompt tokens one image costs. Providers resize large images (about 1.5k
# tokens for a typical vision model, a few thousand for tall full-page screenshots); 4,000 is
# deliberately pessimistic so the per-call and daily caps hold. Documented in decision D128.
IMAGE_TOKENS_ESTIMATE = 4000

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
JPEG_MAGIC = b"\xff\xd8\xff"


def sniff(data: bytes) -> str | None:
    """`image/png` or `image/jpeg` judging by the first bytes, else None."""
    if data.startswith(PNG_MAGIC):
        return "image/png"
    if data.startswith(JPEG_MAGIC):
        return "image/jpeg"
    return None


def is_image_part(part) -> bool:
    return isinstance(part, dict) and part.get("type") == "image"


def check_parts(parts) -> list[dict]:
    """Validated copy of a list of parts; raises AIError. Text parts keep only `text`."""
    if not isinstance(parts, list) or not parts or len(parts) > MAX_PARTS_PER_MESSAGE:
        raise AIError(f"A message with parts needs 1 to {MAX_PARTS_PER_MESSAGE} parts.")
    checked = []
    for part in parts:
        kind = part.get("type") if isinstance(part, dict) else None
        if kind == "text" and isinstance(part.get("text"), str):
            checked.append({"type": "text", "text": part["text"]})
        elif kind == "image":
            data = part.get("data")
            if not isinstance(data, bytes | bytearray) or not data:
                raise AIError("An image part needs its bytes in `data`.")
            data = bytes(data)
            if len(data) > MAX_IMAGE_BYTES:
                raise AIError(f"An image is larger than {MAX_IMAGE_BYTES} bytes.")
            if sniff(data) is None:
                raise AIError("Only PNG and JPEG images are accepted.")
            checked.append({"type": "image", "data": data})
        else:
            raise AIError("A message part must be text or an image.")
    return checked


def count_images(messages) -> int:
    return sum(
        1
        for m in messages
        if isinstance(m.get("content"), list)
        for part in m["content"]
        if is_image_part(part)
    )


def data_url(data: bytes) -> str:
    return f"data:{sniff(data)};base64,{base64.b64encode(data).decode('ascii')}"


def for_provider(messages: list[dict]) -> list[dict]:
    """Messages in the OpenAI-compatible shape (`image_url` parts with data URLs)."""
    out = []
    for message in messages:
        content = message["content"]
        if isinstance(content, list):
            content = [
                {"type": "image_url", "image_url": {"url": data_url(p["data"])}}
                if is_image_part(p)
                else p
                for p in content
            ]
        out.append({**message, "content": content})
    return out
