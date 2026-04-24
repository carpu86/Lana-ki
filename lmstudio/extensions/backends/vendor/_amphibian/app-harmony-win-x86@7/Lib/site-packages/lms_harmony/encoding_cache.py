from typing import Dict
from openai_harmony import (
    HarmonyEncoding,
    HarmonyEncodingName,
    load_harmony_encoding,
)

_ENCODING_CACHE: Dict[str, HarmonyEncoding] = {}


def cached_get_harmony_encoding(
    encoding_name: HarmonyEncodingName,
) -> HarmonyEncoding:
    """
    Get a cached Harmony encoding by its name. If not cached, load it and cache it.
    """
    if encoding_name != "HarmonyGptOss":
        raise ValueError(f"Invalid encodingName: {encoding_name}")
    if encoding_name not in _ENCODING_CACHE:
        encoding = load_harmony_encoding(encoding_name)
        _ENCODING_CACHE[encoding_name] = encoding

    return _ENCODING_CACHE[encoding_name]
