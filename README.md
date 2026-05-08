---

title: HuggingFlow
emoji: 🦌
colorFrom: green
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
license: mit
secrets:
  - name: LLM_MODEL
    description: "Model in provider/model-name format — e.g. openai/gpt-4o, anthropic/claude-sonnet-4-5, google/gemini-2.5-flash"
  - name: LLM_API_KEY
    description: API key for the chosen LLM provider.
  - name: NVIDIA_PROVIDER_JSON
    description: "JSON blob for NVIDIA provider/model configuration, including models and provider settings."
  - name: NVIDIA_API_KEYS
    description: "Comma- or newline-separated NVIDIA API keys used with round-robin rotation and retry on rate limits."
  - name: HF_TOKEN
    description: Hugging Face token (write access) — enables thread backup/restore to a private HF Dataset.
  - name: SERPER_API_KEY
    description: "Serper API key for real Google Search results (recommended). Free tier: 2,500 queries/month."
  - name: AUTH_JWT_SECRET
    description: "JWT signing secret — keeps sessions alive across restarts. Generate: openssl rand -base64 32"
  - name: CLOUDFLARE_WORKERS_TOKEN
    description: "Cloudflare API token — auto-creates an outbound proxy Worker and a keep-awake cron Worker."
---

<div align="center">

# 🦌 HuggingFlow

**[DeerFlow](https://github.com/bytedance/deer-flow) research agent — one-click deploy on Hugging Face Spaces**

[![HF Space](https://img.shields.io/badge/🤗%20Hugging%20Face-Space-yellow)](https://huggingface.co/spaces/somratpro/HuggingFlow)
[![GitHub](https://img.shields.io/badge/GitHub-somratpro%2FHuggingFlow-181717?logo=github)](https://github.com/somratpro/HuggingFlow)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-single--container-2496ED?logo=docker)](Dockerfile)

*Self-hosted deep-research AI · multi-provider LLM · streaming SSE · dataset backup*

</div>

---

## Quick Start

1. Duplicate the Space.
2. Add the required NVIDIA secrets:
   - `LLM_MODEL=nvidia/moonshotai/kimi-k2.6`
   - `NVIDIA_PROVIDER_JSON=<JSON from NVIDIA_QUICK_SETUP.md>`
   - `NVIDIA_API_KEYS=<comma-separated keys>`
3. Rebuild the Space after changing secrets.
4. Open `/workspace`.

For the full NVIDIA setup, model list, and troubleshooting notes, see [NVIDIA_QUICK_SETUP.md](NVIDIA_QUICK_SETUP.md).

---

## Configuration

### Required Secrets

| Secret | Description |
|--------|-------------|
| `LLM_MODEL` | Model in `provider/model-name` format — see [LLM Providers](#llm-providers) |
| `LLM_API_KEY` | API key for the chosen provider |
| `NVIDIA_PROVIDER_JSON` | NVIDIA provider/model JSON blob |
| `NVIDIA_API_KEYS` | Comma- or newline-separated NVIDIA API keys |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SERPER_API_KEY` | — | Google Search via Serper — strongly recommended over DuckDuckGo |
| `TAVILY_API_KEY` | — | Alternative web search (used if Serper not set) |
| `JINA_API_KEY` | — | Better web page fetching via Jina AI |
| `AUTH_JWT_SECRET` | auto-generated | JWT signing secret — set this to keep sessions alive across restarts |
| `HF_TOKEN` | — | Your HF token — enables dataset backup/restore |
| `BACKUP_DATASET_NAME` | `huggingflow-backup` | HF dataset repo name for backups (created automatically) |
| `CUSTOM_BASE_URL` | — | OpenAI-compatible API base URL for any custom/self-hosted provider |
| `SYNC_INTERVAL` | `600` | Seconds between HF Dataset backup syncs |
| `BACKEND_READY_TIMEOUT` | `120` | Seconds to wait for backend startup |
| `FRONTEND_READY_TIMEOUT` | `120` | Seconds to wait for frontend startup |
| `CLOUDFLARE_WORKERS_TOKEN` | — | Cloudflare API token — enables outbound proxy + keep-awake cron |
| `CLOUDFLARE_PROXY_URL` | — | Existing Cloudflare Worker URL (skip auto-setup) |
| `NVIDIA_KEY_COOLDOWN_SECONDS` | `60` | Cooldown time for NVIDIA keys after rate limiting |

---

## NVIDIA Provider Configuration

Use NVIDIA when you want to supply a full provider/model JSON blob and rotate through multiple keys.

Example:

```json
{
  "baseUrl": "https://integrate.api.nvidia.com/v1",
  "api": "openai-completions",
  "models": [
    {
      "id": "moonshotai/kimi-k2.6",
      "name": "Kimi K2.6 (NVIDIA)",
      "reasoning": true,
      "contextWindow": 200000,
      "maxTokens": 16384
    }
  ]
}
```

Set:

- `LLM_MODEL=nvidia/moonshotai/kimi-k2.6`
- `NVIDIA_PROVIDER_JSON=<json above>`
- `NVIDIA_API_KEYS=key1,key2,key3`

Rotation behavior:

- keys are parsed from comma- or newline-separated values
- requests use round-robin selection
- rate-limited keys cool down temporarily
- retries continue with the next key

For the full list of supported NVIDIA models and the exact working JSON, see [NVIDIA_QUICK_SETUP.md](NVIDIA_QUICK_SETUP.md).

---

## Troubleshooting

**"Environment variable {NVIDIA_API_KEYS} not found"**
> Ensure `NVIDIA_API_KEYS` is set in the Space secrets and rebuild the Space after changing it.

**`object async_generator can't be used in 'await' expression`**
> This was fixed in `huggingflow_nvidia.py`. If you still see it, rebuild the Space so the updated image is used.

**UI stuck on one model/mode**
> Rebuild the Space after updating NVIDIA secrets/config. A stale build can keep old config state around.

---

## More Projects

Similar projects by [@somratpro](https://github.com/somratpro) — all free, one-click deploy on HF Spaces:

| Project | What it runs | HF Space | GitHub |
|---------|-------------|----------|--------|
| **HuggingClip** | Paperclip — AI agent orchestration | [Space](https://huggingface.co/spaces/somratpro/HuggingClip) | [Repo](https://github.com/somratpro/HuggingClip) |
| **HuggingClaw** | OpenClaw — Claude Code in the browser | [Space](https://huggingface.co/spaces/somratpro/HuggingClaw) | [Repo](https://github.com/somratpro/HuggingClaw) |
| **HuggingMes** | Hermes — self-hosted agent gateway | [Space](https://huggingface.co/spaces/somratpro/HuggingMes) | [Repo](https://github.com/somratpro/HuggingMes) |
| **Hugging8n** | n8n — workflow & automation platform | [Space](https://huggingface.co/spaces/somratpro/Hugging8n) | [Repo](https://github.com/somratpro/Hugging8n) |
| **HuggingPost** | Postiz — social media scheduler | [Space](https://huggingface.co/spaces/somratpro/HuggingPost) | [Repo](https://github.com/somratpro/HuggingPost) |
