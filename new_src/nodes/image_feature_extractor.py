import sys
import torch
import torchvision

from abc import ABC
from abc import abstractmethod
from PIL.Image import Image

from node import Node
from helpers.storage_helper import StorageHelper
from utils import Utils


class ImageFeatureExtractor(Node):

    PARAMETERS = {
        'input_dir': str,
        'output_dir': str,
        'targets': dict,
        'cuda_id': int,
        'model_id': str
    }

    def __init__(self, input_dir: str, output_dir: str, targets: dict | str, cuda_id: int, model_id: str) -> None:
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.targets = targets if isinstance(
            targets, dict) else StorageHelper.load_targets(targets)
        self.model: ImageToVectorModel = globals()[model_id](cuda_id)

    def run(self) -> None:
        progress = 0
        num_targets = len(self.targets)
        for compound in self.targets.keys():
            progress += 1
            sys.stdout.write(
                f'Processing target {progress} out of {num_targets}\r')
            sys.stdout.flush()
            compound_input_dir = Utils.join_paths(self.input_dir, compound)
            compound_output_dir = Utils.join_paths(self.output_dir, compound)
            Utils.create_dir(compound_output_dir)
            file_names = StorageHelper.list_files(compound_input_dir, False)

            for file_name in file_names:
                file_input_path = Utils.join_paths(
                    compound_input_dir, f'{file_name}.png')
                file_output_path = Utils.join_paths(
                    compound_output_dir, f'{file_name}.pt')

                image = StorageHelper.load_image(file_input_path)
                vector = self.model.extract_vector(image)
                StorageHelper.save_vector(vector, file_output_path)


class ImageToVectorModel(ABC):

    @abstractmethod
    def extract_vector(self, image: Image) -> torch.Tensor:
        pass


# TODO: Understand ViT and add some parameters (e.g. weights, transformation, size)
class VisionTransformer(ImageToVectorModel):

    def __init__(self, cuda_id: int) -> None:
        self.cuda_id = cuda_id
        self.model = torchvision.models.vit_h_14(
            weights=torchvision.models.ViT_H_14_Weights.DEFAULT
        )
        self.model.heads = torch.nn.Sequential(
            *list(self.model.heads.children())[:-1]
        )
        self.model.to(self.cuda_id)

    def extract_vector(self, image: Image) -> torch.Tensor:
        transformations = torchvision.transforms.Compose(
            [
                torchvision.transforms.ToTensor(),
                torchvision.transforms.Normalize(
                    (0.485, 0.456, 0.406),
                    (0.229, 0.224, 0.225)
                ),
                torchvision.transforms.Resize((518, 518))
            ]
        )
        image = transformations(image).float().unsqueeze_(0).to(self.cuda_id)
        return self.model(image).squeeze(0).detach().cpu()
