# Universal Input Hub by Steve Lasmin

An all-in-one ComfyUI workflow node that replaces multiple standard nodes with a single powerful hub. Calculates image dimensions, generates noise, computes sigmas (standard and Flux-optimized), encodes conditioning, and provides sampler objects — all in one place.

**Author:** Steve Lasmin  
**Support:** https://boosty.to/stevelasmin

---

## What It Does

Instead of wiring together **Empty Latent Image**, **CLIP Text Encode**, **KSampler selector**, **noise generator**, and **sigma scheduler** nodes, this single node handles everything.

---

## Inputs (15)

### Resolution & Aspect
| Input | Type | Default | Range | Description |
|-------|------|---------|-------|-------------|
| `max_size` | INT | 1024 | 32–4096 (step 32) | Longest side of the output image in pixels |
| `aspect_ratio` | preset | custom | 11 presets + custom | Choose 1:1, 3:2, 4:3, 16:9, 16:10, 21:9, 2:3, 3:4, 9:16, 9:21, or custom |
| `width_ratio` | INT | 2 | 1–999999 | Custom width component (only when aspect_ratio = custom) |
| `height_ratio` | INT | 3 | 1–999999 | Custom height component (only when aspect_ratio = custom) |
| `multiplier` | dropdown | 32 | 16 / 32 / 64 | Ensures output dimensions are divisible by this value |

### Generation Parameters
| Input | Type | Default | Range | Description |
|-------|------|---------|-------|-------------|
| `seed` | INT | 777 | 0–max uint64 | Random seed for noise generation |
| `steps` | INT | 20 | 1–10000 | Number of sampling steps |
| `cfg` | FLOAT | 4.0 | 0.0–100.0 (step 0.1) | Classifier-Free Guidance scale |
| `sampler` | dropdown | euler | All ComfyUI samplers | Sampling algorithm (euler, dpmpp_2m, etc.) |
| `scheduler` | dropdown | normal | All ComfyUI schedulers | Noise schedule (normal, simple, karras, etc.) |

### Model & Prompts
| Input | Type | Description |
|-------|------|-------------|
| `model` | MODEL | Diffusion model input |
| `clip` | CLIP | CLIP text encoder input |
| `prompt` | STRING (multiline) | Main positive text prompt |
| `trigger_words` | STRING | Words auto-prepended to prompt with ". " separator |
| `negative_prompt` | STRING (multiline) | Text to exclude from generation |

---

## Outputs (20)

| Output | Type | Description |
|--------|------|-------------|
| `width` | INT | Calculated image width in pixels |
| `height` | INT | Calculated image height in pixels |
| `preview` | STRING | Human-readable summary of all settings |
| `seed` | INT | Seed value passthrough |
| `noise` | NOISE | Noise object for SamplerCustomAdvanced |
| `steps` | INT | Steps passthrough |
| `cfg` | FLOAT | CFG passthrough |
| `sampler_name` | STRING | Sampler name as string |
| `sampler` | SAMPLER | Sampler object for advanced samplers |
| `scheduler_name` | STRING | Scheduler name as string |
| `sigmas` | SIGMAS | Standard sigmas from model + scheduler + steps |
| `flux_sigmas` | SIGMAS | Flux-2 optimized sigmas (dimension-aware, no model needed) |
| `model` | MODEL | Model passthrough |
| `prompt` | STRING | Original prompt text |
| `prompt_with_triggers` | STRING | Prompt with trigger words prepended |
| `negative_prompt` | STRING | Negative prompt text |
| `trigger_words` | STRING | Cleaned trigger words (as entered, stripped) |
| `positive` | CONDITIONING | Positive conditioning tensor |
| `negative` | CONDITIONING | Negative conditioning tensor |
| `help` | STRING | Full in-node documentation |

---

## Key Features

- **19 outputs** — everything a sampler needs in one node
- **Flux-2 sigma schedule** — computed from actual output dimensions using time-SNR shift
- **Trigger words** — automatically prepended with proper ". " separator
- **Tooltips on every input** — hover for guidance
- **Clean docstring** — no garbled mixed text
- **Consistent rounding** — width/height calculated once and reused throughout

---

## Installation

1. Navigate to your `ComfyUI/custom_nodes/` directory
2. Clone this repository:
   ```bash
   git clone https://github.com/Eklipsis/universal_input_hub_by_steve_lasmin.git
   ```
3. Restart ComfyUI

The node appears under **utils → Universal Input Hub by Steve Lasmin**.

---

## Example Workflow

1. Load Checkpoint → connect `MODEL` and `CLIP` to this node
2. Set `max_size` to `1024`, `aspect_ratio` to `16:9`, `multiplier` to `32`
3. Type your `prompt` and optional `trigger_words`
4. Connect outputs to `SamplerCustomAdvanced` or standard KSampler

---

## File Structure

```
universal_input_hub_by_steve_lasmin/
├── __init__.py
├── nodes.py
├── README.md
├── LICENSE
├── .gitignore
└── pyproject.toml
```

---

## License

This project is licensed under the **Creative Commons Attribution-NoDerivatives 4.0 International License**.

- ✅ Free to use (personal and commercial)
- ✅ Free to share
- ❌ **Modifications and derivative works are not allowed without permission**

See [LICENSE](LICENSE) for full terms.

To request permission for modifications, contact: **real.eclipse@gmail.com**

---

## Support

If you find this node useful, consider supporting the author:  
https://boosty.to/stevelasmin
