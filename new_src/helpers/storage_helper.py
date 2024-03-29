import csv
import os
import torch
import yaml

from natsort import natsorted
from PIL import Image


class StorageHelper():

    @staticmethod
    def load_targets(file_path: str) -> dict:
        with open(file_path, 'r') as f:
            targets = yaml.safe_load(f)
        return targets

    @staticmethod
    def list_files(directory_path: str, include_extensions: bool) -> list[str]:
        files = natsorted(os.listdir(directory_path))
        if not include_extensions:
            files = [file.split('.')[0] for file in files]
        return files

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

    @staticmethod
    def load_csv(file_path: str) -> list:
        data = []
        with open(file_path, 'r') as f:
            csv_reader = csv.DictReader(f)
            header = csv_reader.fieldnames
            for row in csv_reader:
                data.append(row)
        return data

    @staticmethod
    def save_csv(header: list, values: list, file_path: str) -> None:
        with open(file_path, 'w') as f:
            csv_writer = csv.DictWriter(f, fieldnames=header)
            csv_writer.writeheader()
            csv_writer.writerows(values)
