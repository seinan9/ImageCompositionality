from scipy.stats import spearmanr

from core.node import Node
from core.utils import create_dir, join_paths
from task.utils import load_csv, save_csv

class CorrelationCalculator(Node):

    PARAMETERS = {
        'input_file_0': str,
        'input_file_1': str,
        'columns_0': list,
        'columns_1': list,
        'output_dir': str,
        'output_header': list,
        'measure': str
    }

    def __init__(self, input_file_0: str, input_file_1: str, columns_0: list, columns_1: list,  output_dir: str, output_header: list, measure: str) -> None:
        self.data_0 = load_csv(input_file_0)
        self.data_1 = load_csv(input_file_1)

        # Identify the headers that are supposed to be correlated
        header_0 = list(self.data_0[0].keys())
        header_1 = list(self.data_1[0].keys())
        self.header_0 = [header_0[col] for col in columns_0]
        self.header_1 = [header_1[col] for col in columns_1]

        self.output_dir = output_dir
        self.output_header = output_header
        create_dir(output_dir)

        self.measure = getattr(self, measure)

    def run(self) -> None:
        correlations = {}
        for i in range(len(self.output_header)):
            values_0 = [value[self.header_0[i]] for value in self.data_0]
            values_1 = [value[self.header_1[i]] for value in self.data_1]
            correlation = round(self.measure(values_0, values_1), 3)
            correlations[self.output_header[i]] = correlation

        output_file = join_paths(self.output_dir, 'correlations.csv')
        save_csv(self.output_header, [correlations], output_file)

    def spearman(self, values_0: list, values_1: list) -> float:
        correlation, p_value = spearmanr(values_0, values_1)
        return correlation
