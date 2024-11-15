import logging
import torch

from abc import ABC
from abc import abstractmethod
from diffusers.pipelines.auto_pipeline import AutoPipelineForText2Image
from diffusers import StableDiffusionXLPipeline, Transformer2DModel, PixArtSigmaPipeline
import diffusers
from PIL.Image import Image

from core.node import Node
from core.utils import create_dir, join_paths
from task.utils import load_targets, save_image, load_sentences


class AdvancedImageGenerator(Node):

    PARAMETERS = {
        'output_dir': str,
        'targets': dict | str,
        'prompts_dir': str,
        'seed': int,
        'cuda_id': int,
        'num_images': int,
        'model_type': str,
        'model_path': str,
        'steps': int,
        'cfg': float
    }

    def __init__(self, output_dir: str, targets: dict | str, prompts_dir: str, seed: int, cuda_id: int, num_images: int, model_type: str, model_path: str, steps: int, cfg: float) -> None:
        self.logger = logging.getLogger(__name__)
        self.output_dir = output_dir
        self.targets = targets if isinstance(
            targets, dict) else load_targets(targets)
        self.prompts_dir = prompts_dir
        self.seed = seed
        self.num_images = num_images
        self.steps = steps
        self.cfg = cfg
        self.model: TextToImageModel = globals(
        )[model_type](model_path, cuda_id)

    def run(self) -> None:
        progress = 0
        num_targets = len(self.targets)
        for compound, constituents in self.targets.items():
            progress += 1
            self.logger.progress(
                f'Processing targets {progress} out of {num_targets}')
            compound_output_dir = join_paths(self.output_dir, compound)
            create_dir(compound_output_dir)

            for target in [compound] + constituents:
                if target == compound:
                    target_sentences_file = join_paths(self.prompts_dir, f'{constituents[0]}_{constituents[1]}')
                else:
                    target_sentences_file = join_paths(self.prompts_dir, target)
                sentences = load_sentences(target_sentences_file)
                num_images = min(self.num_images, len(sentences))
                for i in range(0, num_images):
                    image = self.model.generate_image(
                        seed=self.seed + i,
                        prompt=sentences[i],
                        steps=self.steps,
                        cfg=self.cfg
                    )
                    image_output_path = join_paths(
                        compound_output_dir, f'{target}_{i+1}.png')
                    save_image(image, image_output_path)


class TextToImageModel(ABC):

    @abstractmethod
    def generate_image(self, seed: int, prompt: str, steps: int, cfg: float) -> Image:
        pass


class StableDiffusionXL(TextToImageModel):

    def __init__(self, model_path: str, cuda_id: str) -> None:
        diffusers.utils.logging.disable_progress_bar()
        self.pipe = StableDiffusionXLPipeline.from_single_file(
            pretrained_model_link_or_path=model_path,
            torch_dtype=torch.float16,
            use_safetensors=True
        )
        self.pipe.to(f'cuda:{cuda_id}')
        self.pipe.set_progress_bar_config(disable=True)

    def generate_image(self, seed: int, prompt: str, steps: int, cfg: float) -> Image:
        generator = torch.manual_seed(seed)
        with torch.no_grad():
            return self.pipe(
                prompt=prompt,
                num_inference_steps=steps,
                classifier_guidance=cfg,
                generator=generator,
                width=1024,
                height=1024
            ).images[0]


class PixArtSigma(TextToImageModel):

    def __init__(self, model_path: str, cuda_id: str) -> None:
        transformer = Transformer2DModel.from_pretrained(
            pretrained_model_name_or_path="PixArt-alpha/PixArt-Sigma-XL-2-1024-MS", 
            subfolder='transformer', 
            torch_dtype=torch.float16,
            use_safetensors=True,
        )

        self.pipe = PixArtSigmaPipeline.from_pretrained(
            pretrained_model_name_or_path="PixArt-alpha/pixart_sigma_sdxlvae_T5_diffusers",
            transformer=transformer,
            torch_dtype=torch.float16,
            use_safetensors=True,
        )
        self.pipe.to(f'cuda:{cuda_id}')
        self.pipe.set_progress_bar_config(disable=True)

    def generate_image(self, seed: int, prompt: str, steps: int, cfg: float) -> Image:
        generator = torch.manual_seed(seed)
        with torch.no_grad():
            return self.pipe(
                prompt=prompt,
                num_inference_steps=steps,
                classifier_guidance=cfg,
                generator=generator,
                width=1024,
                height=1024
            ).images[0]
