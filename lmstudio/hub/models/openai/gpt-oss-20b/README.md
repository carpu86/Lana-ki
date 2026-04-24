## gpt-oss

Designed for lower latency and specialized or local deployment, the model has 21B total parameters with only 3.6B active at a time. Thanks to native MXFP4 quantization for the MoE layer, it runs efficiently and it's capable of operating within 16GB of memory.

This model is released under a permissive Apache 2.0 license and it features configurable reasoning effort—low, medium, or high, so users can balance output quality and latency based on their needs. The model offers full chain-of-thought visibility to support easier debugging and increased trust, though this output is not intended for end users. It is fully fine-tunable, enabling adaptation to specific tasks or domains, and includes native agentic capabilities such as function calling, web browsing, Python execution, and structured outputs.

This model supports a context length of 131k.
