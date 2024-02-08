import argparse

from helpers.storage_helper import StorageHelper
from txt2img import Txt2Img

class Runner():

    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-f', '--file', default='./default.json', help='A json file containing the run parameters.')

        try:
            args = parser.parse_args()                
        except argparse.ArgumentError as e:
            print(e)

        self.params = StorageHelper.load_params(args.file)
        StorageHelper.set_output_dir(self.params["output_dir"])
        StorageHelper.create_data_dir()
        StorageHelper.save_params(self.params)

    def run(self):
        Txt2Img.generate_simple_dataset(self.params["compound"], self.params["constituents"], self.params["num_images"], self.params["txt2img_model_id"], self.params["txt2img_model_params"])

if __name__ == "__main__":
    runner = Runner()
    runner.run()