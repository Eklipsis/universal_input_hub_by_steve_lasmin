# Universal Input Hub by Steve Lasmin
# https://boosty.to/stevelasmin

import math
import torch
import comfy.sample
import comfy.samplers


class Noise_RandomNoise:
    def __init__(self, seed):
        self.seed = seed

    def generate_noise(self, input_latent):
        latent_image = input_latent["samples"]
        batch_inds = input_latent["batch_index"] if "batch_index" in input_latent else None
        return comfy.sample.prepare_noise(latent_image, self.seed, batch_inds)


def generalized_time_snr_shift(t, mu, sigma):
    return math.exp(mu) / (math.exp(mu) + (1 / t - 1) ** sigma)

def compute_empirical_mu(image_seq_len, num_steps):
    a1, b1 = 8.73809524e-05, 1.89833333
    a2, b2 = 0.00016927, 0.45666666

    if image_seq_len > 4300:
        mu = a2 * image_seq_len + b2
        return float(mu)

    m_200 = a2 * image_seq_len + b2
    m_10 = a1 * image_seq_len + b1

    a = (m_200 - m_10) / 190.0
    b = m_200 - 200.0 * a
    mu = a * num_steps + b

    return float(mu)

def get_flux_schedule(num_steps, image_seq_len):
    mu = compute_empirical_mu(image_seq_len, num_steps)
    timesteps = torch.linspace(1, 0, num_steps + 1)
    timesteps = generalized_time_snr_shift(timesteps, mu, 1.0)
    return timesteps


class Universal_Input_Hub_by_Steve_Lasmin:
    """
    Universal Input Hub — an all-in-one ComfyUI workflow node.

    Calculates image dimensions from aspect ratio and max size,
    then generates noise, sigmas (standard + Flux), conditioning,
    and sampler objects for generation workflows.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "max_size": ("INT", {
                    "default": 1024,
                    "min": 32,
                    "max": 4096,
                    "step": 32,
                    "display": "number",
                    "tooltip": "Maximum dimension in pixels. The longest side of the image will match this value."
                }),
                "aspect_ratio": (["custom", "1:1", "3:2", "4:3", "16:9", "16:10", "21:9", "2:3", "3:4", "9:16", "9:21"], {
                    "default": "custom",
                    "tooltip": "Select a preset aspect ratio, or choose 'custom' to define your own via width_ratio and height_ratio."
                }),
                "width_ratio": ("INT", {
                    "default": 2,
                    "min": 1,
                    "max": 999999,
                    "step": 1,
                    "display": "number",
                    "tooltip": "Custom width component of the aspect ratio. Only used when aspect_ratio is set to 'custom'."
                }),
                "height_ratio": ("INT", {
                    "default": 3,
                    "min": 1,
                    "max": 999999,
                    "step": 1,
                    "display": "number",
                    "tooltip": "Custom height component of the aspect ratio. Only used when aspect_ratio is set to 'custom'."
                }),
                "multiplier": (["16", "32", "64"], {
                    "default": "32",
                    "tooltip": "Round width and height to be divisible by this value. Use 64 for SD 1.5, 32 for SDXL, 16 for Flux."
                }),
                "seed": ("INT", {
                    "default": 777,
                    "min": 0,
                    "max": 0xffffffffffffffff,
                    "step": 1,
                    "display": "number",
                    "tooltip": "Random seed for noise generation. Use 'control after generate' to randomize, increment, or keep fixed."
                }),
                "steps": ("INT", {
                    "default": 20,
                    "min": 1,
                    "max": 10000,
                    "step": 1,
                    "display": "number",
                    "tooltip": "Number of sampling steps. Higher values = more detail but slower generation."
                }),
                "cfg": ("FLOAT", {
                    "default": 4.0,
                    "min": 0.0,
                    "max": 100.0,
                    "step": 0.1,
                    "round": 0.01,
                    "display": "number",
                    "tooltip": "Classifier-Free Guidance scale. Higher = stronger prompt adherence. Flux works well at 1.0-4.0, SDXL at 7.0-8.0."
                }),
                "sampler": (comfy.samplers.KSampler.SAMPLERS, {
                    "default": "euler",
                    "tooltip": "Sampling algorithm. 'euler' is fast and reliable. 'dpmpp_2m' is higher quality."
                }),
                "scheduler": (comfy.samplers.KSampler.SCHEDULERS, {
                    "default": "normal",
                    "tooltip": "Noise schedule. 'normal' is standard. 'simple' works well with Flux. 'karras' for SDXL."
                }),
                "model": ("MODEL", {
                    "tooltip": "The diffusion model. Required for standard sigmas calculation and model passthrough."
                }),
                "clip": ("CLIP", {
                    "tooltip": "The CLIP text encoder. Required to convert text prompts into conditioning tensors."
                }),
                "prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "dynamicPrompts": True,
                    "tooltip": "Main positive prompt describing what you want to generate."
                }),
                "trigger_words": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "dynamicPrompts": True,
                    "tooltip": "Trigger words prepended to the prompt with '. ' separator. Leave empty to use prompt only."
                }),
                "negative_prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "dynamicPrompts": True,
                    "tooltip": "Negative prompt describing what you want to exclude from the image."
                }),
            }
        }

    RETURN_TYPES = ("INT", "INT", "STRING", "INT", "NOISE", "INT", "FLOAT", "STRING", "SAMPLER", "STRING", "SIGMAS", "SIGMAS", "MODEL", "STRING", "STRING", "STRING", "STRING", "CONDITIONING", "CONDITIONING", "STRING")
    RETURN_NAMES = ("width", "height", "preview", "seed", "noise", "steps", "cfg", "sampler_name", "sampler", "scheduler_name", "sigmas", "flux_sigmas", "model", "prompt", "prompt_with_triggers", "negative_prompt", "trigger_words", "positive", "negative", "help")
    FUNCTION = "calculate"
    CATEGORY = "utils"
    OUTPUT_NODE = True

    def calculate(self, max_size, aspect_ratio, width_ratio, height_ratio, multiplier, seed, steps, cfg, sampler, scheduler, model, clip, prompt, trigger_words, negative_prompt):
        # Parse preset if not custom
        if aspect_ratio != "custom":
            w, h = aspect_ratio.split(":")
            width_ratio = int(w)
            height_ratio = int(h)

        # Convert multiplier from string to int
        multiplier = int(multiplier)

        aspect = width_ratio / height_ratio

        # max_size = maximum dimension (longest side)
        if aspect >= 1:
            width = max_size
            height = max_size / aspect
        else:
            height = max_size
            width = max_size * aspect

        # Round to nearest multiple of multiplier
        width = round(width / multiplier) * multiplier
        height = round(height / multiplier) * multiplier

        # Ensure minimum dimensions
        width = max(multiplier, width)
        height = max(multiplier, height)

        # Store rounded dimensions
        rounded_width = int(width)
        rounded_height = int(height)

        # Create proper NOISE object from seed
        noise = Noise_RandomNoise(seed)

        # Convert sampler name to SAMPLER object
        sampler_obj = comfy.samplers.sampler_object(sampler)

        # Calculate standard sigmas from model + scheduler + steps
        sigmas = comfy.samplers.calculate_sigmas(
            model.get_model_object("model_sampling"),
            scheduler,
            steps
        ).cpu()

        # Calculate Flux 2 sigmas from ROUNDED dimensions + steps (no model needed)
        seq_len = round((rounded_width * rounded_height) / (16 * 16))
        flux_sigmas = get_flux_schedule(steps, seq_len)

        # Build prompt plus trigger words
        trigger_stripped = trigger_words.strip()
        if trigger_stripped:
            trigger_words_output = trigger_stripped + ". "
            prompt_with_triggers = trigger_words_output + prompt
        else:
            trigger_words_output = ""
            prompt_with_triggers = prompt

        # Encode positive conditioning from "prompt_with_triggers"
        positive_tokens = clip.tokenize(prompt_with_triggers)
        positive = clip.encode_from_tokens_scheduled(positive_tokens)

        # Encode negative conditioning from "negative_prompt"
        negative_tokens = clip.tokenize(negative_prompt)
        negative = clip.encode_from_tokens_scheduled(negative_tokens)

        # Create preview string
        preview_text = f"Width: {rounded_width} px  |  Height: {rounded_height} px  |  Aspect: {width_ratio}:{height_ratio}  |  Multiplier: {multiplier}  |  Seed: {seed}  |  Steps: {steps}  |  CFG: {cfg}  |  Sampler: {sampler}  |  Scheduler: {scheduler}"

        # Build help text
        help_text = (
            "=== INPUTS ===\n"
            "max_size: Maximum dimension in pixels (longest side).\n"
            "aspect_ratio: Preset or custom aspect ratio.\n"
            "width_ratio / height_ratio: Custom aspect components (only when aspect_ratio=custom).\n"
            "multiplier: Round dimensions to multiples of 16/32/64.\n"
            "seed: Random seed for noise. Use control_after_generate widget.\n"
            "steps: Sampling steps (1-10000).\n"
            "cfg: Guidance scale. Flux: 1-4, SDXL: 7-8.\n"
            "sampler: Sampling algorithm (euler, dpmpp_2m, etc.).\n"
            "scheduler: Noise schedule (normal, simple, karras, etc.).\n"
            "model: Diffusion model input.\n"
            "clip: CLIP text encoder input.\n"
            "prompt: Main positive text prompt.\n"
            "trigger_words: Words prepended to prompt with '. '.\n"
            "negative_prompt: Text to exclude from generation.\n\n"
            "=== OUTPUTS ===\n"
            "width / height: Calculated pixel dimensions.\n"
            "preview: Human-readable summary string.\n"
            "seed: Integer seed value.\n"
            "noise: NOISE object for SamplerCustomAdvanced.\n"
            "steps / cfg: Passthrough values.\n"
            "sampler_name / sampler: String name and SAMPLER object.\n"
            "scheduler_name: String scheduler name.\n"
            "sigmas: Standard SIGMAS tensor (needs model).\n"
            "flux_sigmas: Flux-2 optimized SIGMAS (dimension-aware, no model needed).\n"
            "model: MODEL passthrough.\n"
            "prompt / prompt_with_triggers / negative_prompt: Text outputs.\n"
            "positive / negative: CONDITIONING tensors for sampler inputs.\n"
            "help: This text."
        )

        return (
            rounded_width,
            rounded_height,
            preview_text,
            int(seed),
            noise,
            int(steps),
            float(cfg),
            sampler,
            sampler_obj,
            scheduler,
            sigmas,
            flux_sigmas,
            model,
            prompt,
            prompt_with_triggers,
            negative_prompt,
            trigger_words_output,
            positive,
            negative,
            help_text
        )


NODE_CLASS_MAPPINGS = {
    "Universal_Input_Hub_by_Steve_Lasmin": Universal_Input_Hub_by_Steve_Lasmin,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Universal_Input_Hub_by_Steve_Lasmin": "Universal Input Hub by Steve Lasmin",
}
