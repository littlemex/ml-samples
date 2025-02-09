#!/bin/bash
uvx --python 3.10 pdf2zh -li en -lo ja -t 1 -s "ollama:gemma2:2b-instruct-q4_K_M;hf.co/mmnga/cyberagent-DeepSeek-R1-Distill-Qwen-32B-Japanese-gguf:latest" $1
