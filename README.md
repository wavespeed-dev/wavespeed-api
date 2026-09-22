# WaveSpeed API — Python client

[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/) [![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE) [![Hosted on Synexa](https://img.shields.io/badge/hosted%20on-Synexa-6366f1.svg)](https://synexa.ai/explore/black-forest-labs/flux-schnell?utm_source=github&utm_medium=ugc&utm_campaign=wavespeed-dev&utm_content=readme-badge&utm_term=tier-c)

WaveSpeed is an inference platform that specialises in fast image and video generation, serving models such as FLUX, Wan and Seedance behind a single API with an emphasis on latency and price per run. This repository is a Python client for the same class of workload through WaveSpeed-class hosted endpoints on Synexa: FLUX.1 schnell for sub-second images, Wan 2.2 for image-to-video, and Seedance 2.5 for text-to-video with audio, all callable with one `pip install` and one API token.

You get a blocking `run()` that takes a prompt and returns the result URL, a non-blocking create-and-poll path for batches, and webhook delivery for services that would rather be called back. The client has a single runtime dependency and no model weights. It is aimed at developers building high-volume image pipelines, thumbnail and preview generation, or video features where throughput and cost per call matter more than the last increment of quality.

> **Try it now:** [https://synexa.ai/explore/black-forest-labs/flux-schnell](https://synexa.ai/explore/black-forest-labs/flux-schnell?utm_source=github&utm_medium=ugc&utm_campaign=wavespeed-dev&utm_content=readme-top&utm_term=tier-c) — the hosted model behind this client. New accounts get a free trial credit.

## Contents

- [Why this client](#why-this-client)
- [Installation](#installation)
- [Quickstart](#quickstart)
- [Hosted models](#hosted-models)
- [Parameters](#parameters)
- [Advanced usage](#advanced-usage)
- [About WaveSpeed](#about-wavespeed)
- [Use cases](#use-cases)
- [FAQ](#faq)
- [License](#license)

## Why this client

- **Cost at volume.** `black-forest-labs/flux-schnell` is billed at $0.0015 per run, so a million images costs $1,500; matching that on rented GPUs means keeping a batched server saturated around the clock.
- **No GPU fleet to size.** FLUX.1 schnell is a 12B-parameter model that wants a 24 GB-class GPU in bf16, and Wan 2.2 14B needs an 80 GB-class GPU for video. The endpoints run on Synexa's fleet and scale with your queue.
- **No cold start.** The models stay resident; the first request after an idle night costs the same as the thousandth, and there is no checkpoint to load into memory on your side.
- **Hosted-only models beside open ones.** Seedance 2.5 has no public weights at all, so a hosted endpoint is the only route, and this client gives it the same interface as the open-weights models.

## Installation

```bash
pip install git+https://github.com/wavespeed-dev/wavespeed-api.git
```

Then set your API key (create one at [synexa.ai](https://synexa.ai?utm_source=github&utm_medium=ugc&utm_campaign=wavespeed-dev&utm_content=readme-apikey&utm_term=tier-c)):

```bash
export SYNEXA_API_KEY="sk-..."
```

## Quickstart

```python
import wavespeed_api

output = wavespeed_api.run({
    "prompt": "A cinematic shot of a lighthouse at dawn, soft fog, warm light"
})
print(output)   # URL(s) of the generated result
```

Or with an explicit client:

```python
from wavespeed_api import Client

client = Client(api_key="sk-...")
output = client.run({"prompt": "A cinematic shot of a lighthouse at dawn, soft fog, warm light"})
```

## Hosted models

| Model | Category | What it does | Price / run |
|---|---|---|---|
| [`black-forest-labs/flux-schnell`](https://synexa.ai/explore/black-forest-labs/flux-schnell?utm_source=github&utm_medium=ugc&utm_campaign=wavespeed-dev&utm_content=readme-models&utm_term=tier-c) | text-to-image | The fastest image generation model tailored for local development and personal use | $0.0015 |
| [`tongyi/wan2.2`](https://synexa.ai/explore/tongyi/wan2.2?utm_source=github&utm_medium=ugc&utm_campaign=wavespeed-dev&utm_content=readme-models&utm_term=tier-c) | image-to-video | Generate 5s 480p videos using Wan 2.2 14B. A comprehensive video foundation models that pushes the boundaries of video generation. | $0.2 |
| [`bytedance/seedance-2.5`](https://synexa.ai/explore/bytedance/seedance-2.5?utm_source=github&utm_medium=ugc&utm_campaign=wavespeed-dev&utm_content=readme-models&utm_term=tier-c) | text-to-video | Seedance 2.5 generates a single-shot video of up to 30 seconds from a text prompt, with synchronised audio. | $0.473 |

The default model is **`black-forest-labs/flux-schnell`**; pass `model="owner/name"` to `run()` to use another one from the table.

## Parameters

### `black-forest-labs/flux-schnell`

| Field | Type | Required | Default | Range | Description |
|---|---|---|---|---|---|
| `seed` | integer | no | `random` | — | Random seed. Set for reproducible generation |
| `prompt` | string | yes | `black forest gateau cake spelling out th…` | — | Text prompt for image generation |
| `go_fast` | boolean | no | `True` | — | Run faster predictions with model optimized for speed (currently fp8 quantized); disable to run in original bf16 |
| `megapixels` | string | no | `1` | 1, 0.25 | Approximate number of megapixels for generated image |
| `num_outputs` | integer | no | `1` | 1, 4 | Number of outputs to generate |
| `aspect_ratio` | string | no | `1:1` | 1:1, 16:9, 21:9, 3:2, 2:3, 4:5, 5:4, 3:4, 4:3, 9:16, 9:21 | Aspect ratio for the generated image |
| `output_format` | string | no | `webp` | webp, jpg, png | Format of the output images |
| `output_quality` | integer | no | `80` | 0, 100 | Quality when saving the output images, from 0 to 100. 100 is best quality, 0 is lowest quality. Not relevant for .png outputs |
| `num_inference_steps` | integer | no | `4` | 1, 4 | Number of denoising steps. 4 is recommended, and lower number of steps produce lower quality outputs, faster. |
| `disable_safety_checker` | boolean | no | `False` | — | Disable safety checker for generated images. |

### `tongyi/wan2.2`

| Field | Type | Required | Default | Range | Description |
|---|---|---|---|---|---|
| `prompt` | string | yes | `A woman is talking` | — | Input prompt |
| `input_image` | file | yes | `https://files.synexa.ai/models/wan-image…` | — | Input image to start generating from |
| `aspect_ratio` | string | no | `9:16` | 9:16, 1:1, 16:9 | Video Resolution |
| `seed` | integer | no | `random` | — | Random seed. Leave blank to randomize the seed |
| `num_frames` | integer | no | `81` | 1, 81 | Video Frames |

### `bytedance/seedance-2.5`

| Field | Type | Required | Default | Range | Description |
|---|---|---|---|---|---|
| `prompt` | string | yes | `A lone fisherman rows out at dawn across…` | — | The text prompt used to generate the video |
| `resolution` | string | no | `720p` | 480p, 720p, 1080p | Video resolution - 480p for faster generation, 720p for balance, 1080p for high quality. |
| `duration` | string | no | `auto` | auto, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 1… | Duration of the video in seconds. Supports 4 to 30 seconds, or auto to let the model decide based on the prompt. |
| `aspect_ratio` | string | no | `auto` | auto, 21:9, 16:9, 4:3, 1:1, 3:4, 9:16 | The aspect ratio of the generated video. Use 16:9 for landscape, 9:16 for portrait/vertical, 1:1 for square, 21:9 for ultrawide cinematic, or auto to let the model decide. |
| `generate_audio` | boolean | no | `True` | — | Whether to generate synchronized audio for the video, including sound effects, ambient sounds, and lip-synced speech. The cost of video generation is the same regardless of whether audio is generated or not. |
| `bitrate_mode` | string | no | `standard` | standard, high | Output bitrate mode. 'high' requests a higher-quality, larger-file encode from the model; 'standard' uses the default bitrate. |

## Advanced usage

**Submit without blocking, then poll:**

```python
prediction = client.run(input, wait=False)      # returns immediately
prediction = client.wait(prediction, timeout=300)
print(prediction["output"])
```

**Webhook on completion:**

```python
client.run(input, wait=False, webhook="https://your-app.example/hooks/synexa")
```

**Errors:**

```python
from wavespeed_api import ModelError, PredictionTimeout

try:
    output = client.run(input)
except ModelError as e:
    print("failed:", e, e.prediction and e.prediction.get("id"))
except PredictionTimeout:
    print("still running — poll later")
```

Status values you will see on a prediction: `starting` → `processing` → `succeeded` | `failed`.

## About WaveSpeed

WaveSpeed ([wavespeed.ai](https://wavespeed.ai)) is an AI inference platform focused on speed. It hosts a catalogue of image and video models from third parties, including the FLUX family from Black Forest Labs, Alibaba's Wan video models, ByteDance's Seedance and others, and competes on generation latency and per-run price rather than on training its own models. The team is also associated with open-source work on accelerating diffusion transformer inference. Developers use it as a drop-in backend for products that call many generations per user session.

The endpoints exposed by this client cover the same three workloads. `black-forest-labs/flux-schnell` is Black Forest Labs' open-weights FLUX.1 [schnell] model, a 12B-parameter rectified-flow transformer distilled to produce an image in around four denoising steps; the endpoint exposes `aspect_ratio`, `megapixels`, `num_outputs`, `num_inference_steps`, `seed`, an fp8 `go_fast` switch and output format and quality controls. `tongyi/wan2.2` is Alibaba's open-weights Wan 2.2 14B video model, here in image-to-video form, producing a 5-second 480p clip from an input image and a prompt. `bytedance/seedance-2.5` is ByteDance's proprietary text-to-video model, generating a single-shot clip of 4 to 30 seconds at up to 1080p with synchronised audio.

Typical outputs are large sets of draft images, thumbnails and previews from FLUX schnell; short animated loops and product motion from Wan 2.2; and longer narrative or ad clips with sound from Seedance. Limits to plan for: schnell trades some detail and prompt adherence for speed compared with larger FLUX variants, Wan 2.2 on this endpoint is fixed at 5 seconds and 480p, and Seedance is billed at $0.473 per run, several hundred times the price of an image.

This client does not talk to WaveSpeed. The hosted endpoints it uses are `black-forest-labs/flux-schnell`, `tongyi/wan2.2` and `bytedance/seedance-2.5` on Synexa, which provide the same models WaveSpeed serves but through Synexa's API and billing. FLUX.1 [schnell] and Wan 2.2 are open-weights models you can also self-host from their official releases; WaveSpeed's own platform, catalogue and pricing are at [wavespeed.ai](https://wavespeed.ai).

**Official project:** https://wavespeed.ai

## Use cases

- **Bulk draft images** — call `run()` on `black-forest-labs/flux-schnell` with `num_outputs` set to 4 and `go_fast` on to fill a moodboard for fractions of a cent.
- **Thumbnails and previews** — generate low-`megapixels` images per listing or article through the poll path, then upscale only the ones that ship.
- **Reproducible variants** — fix `seed` and change one word in the prompt to produce controlled A/B image sets.
- **Animated product loops** — pass a packshot as `input_image` to `tongyi/wan2.2` with a short motion prompt for a 5-second clip.
- **Ads with sound** — route final-quality briefs to `bytedance/seedance-2.5` with `generate_audio` on and a 16:9 or 9:16 `aspect_ratio`.
- **Image-then-video pipelines** — generate a frame with FLUX schnell, then feed it to Wan 2.2 in the same script and receive both results by webhook.

## FAQ

**Is there a WaveSpeed API?**

Yes. WaveSpeed's own API is at wavespeed.ai. This client does not call it; it calls hosted endpoints on Synexa that serve the same models, `black-forest-labs/flux-schnell`, `tongyi/wan2.2` and `bytedance/seedance-2.5`, through Synexa's API and billing.

**How much does WaveSpeed-class inference cost through this client?**

`black-forest-labs/flux-schnell` is billed at $0.0015 per run, `tongyi/wan2.2` at $0.20 per run and `bytedance/seedance-2.5` at $0.473 per run. There is no subscription; you pay per completed job.

**Can I run these models without a GPU?**

With this client, yes; generation happens on Synexa's GPUs and your machine only needs Python and network access. FLUX.1 schnell and Wan 2.2 have open weights and can be self-hosted on a suitable GPU; Seedance 2.5 is hosted-only.

**Does this client work with ComfyUI or local FLUX weights?**

No. It does not load checkpoints or drive ComfyUI; it only calls the hosted endpoints. If you already run FLUX locally, this client is for offloading volume, not for controlling your local install.

**What input formats does it accept?**

FLUX schnell requires `prompt`, with optional `aspect_ratio`, `megapixels`, `num_outputs`, `num_inference_steps`, `seed`, `go_fast`, `output_format`, `output_quality` and `disable_safety_checker`. Wan 2.2 requires `prompt` and `input_image`, with optional `aspect_ratio`, `num_frames` and `seed`. Seedance 2.5 requires `prompt`, with optional `resolution`, `duration` (4 to 30 seconds), `aspect_ratio`, `generate_audio` and `bitrate_mode`.

**Is this the official WaveSpeed SDK?**

No. This is an independent client that wraps hosted endpoints on Synexa. WaveSpeed's official platform and API are at https://wavespeed.ai.

## Related

- [WaveSpeed](https://wavespeed.ai) — the inference platform this client is positioned against
- [Synexa Python client](https://github.com/synexa-ai/synexa-python) — the general-purpose SDK this client builds on
- [black-forest-labs/flux-schnell on Synexa](https://synexa.ai/explore/black-forest-labs/flux-schnell) — four-step FLUX.1 schnell image generation
- [tongyi/wan2.2 on Synexa](https://synexa.ai/explore/tongyi/wan2.2) — Wan 2.2 14B image-to-video
- [bytedance/seedance-2.5 on Synexa](https://synexa.ai/explore/bytedance/seedance-2.5) — text-to-video up to 30 seconds with synchronised audio

## License

MIT. This is an independent, community-maintained client and is not affiliated with or endorsed by the authors of WaveSpeed. Model weights and trademarks belong to their respective owners.


_Last reviewed: 2026-09-22_
