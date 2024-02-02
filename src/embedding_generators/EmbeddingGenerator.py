from abc import ABC, abstractmethod
from PIL import Image


class EmbeddingGenerator(ABC):

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def generate_embedding(self, image: Image) -> list[float]:
        pass
