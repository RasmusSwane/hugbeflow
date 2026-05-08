# HuggingFlow NVIDIA Quick Setup

This note captures the working setup and the most common NVIDIA-specific pitfalls we hit while getting HuggingFlow running.

## What you need in Hugging Face Spaces

Add these as **Settings → Variables and Secrets**:

- `LLM_MODEL`
- `NVIDIA_PROVIDER_JSON`
- `NVIDIA_API_KEYS`

Optional but useful:

- `HF_TOKEN` for dataset backup/restore
- `SERPER_API_KEY` for better web search
- `AUTH_JWT_SECRET` to keep sessions alive across restarts

## Required NVIDIA values

### `LLM_MODEL`
Use an NVIDIA model prefix:

```text
nvidia/moonshotai/kimi-k2.6
```

### `NVIDIA_API_KEYS`
Comma-separated or newline-separated NVIDIA API keys.

Example:

```text
key1,key2,key3
```

### `NVIDIA_PROVIDER_JSON`
Use a minimal JSON blob with all models you want available.

Important:
- Do **not** include `"apiKey": "${NVIDIA_API_KEYS}"`
- The app already rotates keys from the `NVIDIA_API_KEYS` secret
- Keep the JSON valid and compact if you paste it into Spaces secrets

## Working minimal JSON

Paste this as the value of `NVIDIA_PROVIDER_JSON`:

```json
{"baseUrl":"https://integrate.api.nvidia.com/v1","api":"openai-completions","models":[{"id":"moonshotai/kimi-k2.6","name":"Kimi K2.6 (NVIDIA)","reasoning":true,"contextWindow":200000,"maxTokens":16384},{"id":"z-ai/glm5","name":"GLM-5 (NVIDIA)","reasoning":true,"contextWindow":205000,"maxTokens":16384},{"id":"z-ai/glm-5.1","name":"GLM-5.1 (NVIDIA)","reasoning":true,"contextWindow":205000,"maxTokens":16384},{"id":"minimaxai/minimax-m2.1","name":"MiniMax M2.1 (NVIDIA)","reasoning":false,"contextWindow":200000,"maxTokens":8192},{"id":"qwen/qwen3.5-397b-a17b","name":"Qwen 3.5 397B (NVIDIA)","reasoning":true,"contextWindow":200000,"maxTokens":16384,"compat":{"supportsDeveloperRole":false}},{"id":"stepfun-ai/step-3.5-flash","name":"Step 3.5 Flash (NVIDIA)","reasoning":true,"contextWindow":200000,"maxTokens":16384},{"id":"z-ai/glm4.7","name":"GLM 4.7 (NVIDIA)","reasoning":true,"contextWindow":200000,"maxTokens":16384},{"id":"deepseek-ai/deepseek-v3.2","name":"DeepSeek V3.2 (NVIDIA)","reasoning":true,"contextWindow":200000,"maxTokens":8192},{"id":"deepseek-ai/deepseek-v4-pro","name":"DeepSeek V4 Pro (NVIDIA)","reasoning":true,"contextWindow":200000,"maxTokens":8192},{"id":"deepseek-ai/deepseek-v4-flash","name":"DeepSeek V4 Flash (NVIDIA)","reasoning":true,"contextWindow":200000,"maxTokens":16384},{"id":"minimaxai/minimax-m2.5","name":"MiniMax M2.5 (NVIDIA)","reasoning":false,"contextWindow":200000,"maxTokens":8192},{"id":"minimaxai/minimax-m2.7","name":"MiniMax M2.7 (NVIDIA)","reasoning":false,"contextWindow":200000,"maxTokens":8192},{"id":"mistralai/mistral-medium-3.5-128b","name":"Mistral Medium 3.5 128B (NVIDIA)","reasoning":true,"contextWindow":128000,"maxTokens":16384,"compat":{"supportsDeveloperRole":false}},{"id":"meta/llama3-70b-instruct","name":"Llama 3 70B (NVIDIA)","reasoning":false,"contextWindow":8192,"maxTokens":4096},{"id":"mistralai/mixtral-8x22b-instruct-v0.1","name":"Mixtral 8x22B (NVIDIA)","reasoning":false,"contextWindow":65536,"maxTokens":4096},{"id":"qwen/qwen3.5-122b-a10b","name":"Qwen 3.5 122B (NVIDIA)","reasoning":true,"contextWindow":200000,"maxTokens":16384,"compat":{"supportsDeveloperRole":false}},{"id":"nvidia/nemotron-3-super-120b-a12b","name":"Nemotron 3 Super 120B (NVIDIA)","reasoning":true,"contextWindow":200000,"maxTokens":16384},{"id":"nvidia/nemotron-3-nano-omni-30b-a3b-reasoning","name":"Nemotron 3 Nano Omni 30B (NVIDIA)","reasoning":true,"contextWindow":200000,"maxTokens":65536}]}
```

## Why the earlier errors happened

### 1) `Environment variable {NVIDIA_API_KEYS} not found`
This happens when the runtime does not actually receive the `NVIDIA_API_KEYS` secret.

Common causes:
- secret not added in Spaces settings
- wrong secret name
- pasted into `.env.example` instead of Spaces secrets
- stale build/container state

### 2) `object async_generator can't be used in 'await' expression`
This was a code bug in `huggingflow_nvidia.py`.

The streaming path incorrectly awaited an async generator. The fix is to iterate the stream with `async for`.

### 3) UI stuck in one mode/model
This was resolved by rebuilding the Space.

Likely cause:
- stale image or stale generated config
- frontend/backend still using an old cached state
- rebuild forced the updated config to be generated and loaded

## Recommended setup order

1. Set `LLM_MODEL`
2. Set `NVIDIA_PROVIDER_JSON`
3. Set `NVIDIA_API_KEYS`
4. Rebuild the Space
5. Open the app and verify model switching works

## Quick checklist

- [ ] `LLM_MODEL=nvidia/...`
- [ ] `NVIDIA_PROVIDER_JSON` is valid JSON
- [ ] `NVIDIA_API_KEYS` exists and has at least one key
- [ ] no `apiKey: "${NVIDIA_API_KEYS}"` in the JSON
- [ ] Space rebuilt after changing secrets/config
- [ ] all desired models are listed in `models[]`

## Local development note

For local Docker/dev use, the repo reads environment variables too. You can export the same values locally or put them in a `.env` file for your own workflow, but Spaces deployment uses the HF secret UI.
