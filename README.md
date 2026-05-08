# Universal Input Hub by Steve Lasmin

An all-in-one ComfyUI workflow node that calculates image dimensions from aspect ratio **and** generates noise, sigmas, conditioning, and sampler objects — replacing multiple standard nodes with a single powerful hub.

**Author:** Steve Lasmin  
**Support:** https://boosty.to/stevelasmin

## Features

### Resolution & Aspect Ratio
- Set a **maximum dimension** (`max_size`) — the longest side of the output image
- Choose from **11 aspect ratio presets** (1:1, 3:2, 4:3, 16:9, 16:10, 21:9, 2:3, 3:4, 9:16, 9:21) or define a **custom ratio**
- Choose a **multiplier** (16, 32, 64) to ensure dimensions are divisible by VAE/UNet block sizes
- Outputs `width` and `height` as integers

### Generation Parameters
- **Seed** input with default `777`
- **Steps** (1–10000)
- **CFG** scale with fine 0.1 stepping
- **Sampler** dropdown (pulled from ComfyUI's native sampler list)
- **Scheduler** dropdown (pulled from ComfyUI's native scheduler list)

### Model & Conditioning
- Accepts `MODEL` and `CLIP` inputs
- **Positive prompt** with optional **trigger words** (auto-prepended with `". "`)
- **Negative prompt**
- Outputs `positive` and `negative` **CONDITIONING** tensors
- Outputs `noise` as a proper **NOISE** object for `SamplerCustomAdvanced`

### Sigmas
- **Standard sigmas** calculated from model + scheduler + steps
- **Flux sigmas** computed dimension-aware using Flux-2 time-SNR shift (no model required)

### Utility Outputs
- `preview` — human-readable summary of all settings
- `help` — full in-node documentation text
- Passthroughs: `model`, `steps`, `cfg`, `sampler_name`, `sampler`, `scheduler_name`, `prompt`, `prompt_with_triggers`, `negative_prompt`

## Installation

1. Navigate to your `ComfyUI/custom_nodes/` directory
2. Clone this repository:
   ```bash
   git clone https://github.com/Eklipsis/universal_input_hub_by_steve_lasmin.git
   ```
3. Restart ComfyUI

## Usage

The node appears under **utils → Universal Input Hub by Steve Lasmin**.

Connect your `MODEL` and `CLIP` inputs, type your prompt, choose an aspect ratio, and the node outputs everything needed to feed directly into a sampler.

### Example Workflow

1. Load Checkpoint → connect `MODEL` and `CLIP` to this node
2. Set `max_size` to `1024`, `aspect_ratio` to `16:9`, `multiplier` to `32`
3. Type your `prompt` and optional `trigger_words`
4. Connect outputs to `SamplerCustomAdvanced` or standard KSampler

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

## License

This project is licensed under the **Creative Commons Attribution-NoDerivatives 4.0 International License**.

- ✅ Free to use (personal and commercial)
- ✅ Free to share
- ❌ **Modifications and derivative works are not allowed without permission**

See [LICENSE](LICENSE) for full terms.

To request permission for modifications, contact: **real.eclipse@gmail.com**

## Support

If you find this node useful, consider supporting the author:  
https://boosty.to/stevelasmin
