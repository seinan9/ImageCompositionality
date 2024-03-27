import os
import torch
import yaml

from natsort import natsorted
from PIL import Image


class StorageHelper():

    @staticmethod
    def create_dir(directory_path: str) -> None:
        os.makedirs(directory_path)

    @staticmethod
    def load_targets(targets_file: str) -> dict:
        with open(targets_file, 'r') as f:
            targets = yaml.safe_load(f)
        return targets

    @staticmethod
    def list_files(directory_path: str) -> list[str]:
        file_names = natsorted([file_name.split('.')[0]
                               for file_name in os.listdir(directory_path)])
        return file_names

    @staticmethod
    def load_image(file_path: str) -> Image.Image:
        image = Image.open(file_path)
        return image

    @staticmethod
    def save_image(image: Image.Image, file_path: str) -> None:
        image.save(file_path)

    @staticmethod
    def load_vector(file_path: str) -> torch.Tensor:
        vector = torch.load(file_path)
        return vector

    @staticmethod
    def save_vector(vector: torch.Tensor, file_path: str) -> None:
        torch.save(vector, file_path)
