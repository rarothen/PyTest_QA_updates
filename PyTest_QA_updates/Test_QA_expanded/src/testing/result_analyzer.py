import json
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import statistics

from config.logger_config import logger


class ResultAnalyzer:
    def __init__(self, data: list[float] = None):
        if not data:
            logger.warning("Data list is empty. Analysis will be skipped.")
        elif len(data) == 0:
            raise ValueError("Data list cannot be empty.")
        self.data = data

    def analyze(self):
        """
        Performs statistical analysis on the measurement data and returns a dictionary of results.
        :return: Dictionary containing mean, median, standard deviation, min, and max of the
        """
        average = sum(self.data) / len(self.data)
        median = sorted(self.data)[len(self.data) // 2]
        std = statistics.stdev(self.data)
        minimum = min(self.data)
        maximum = max(self.data)
        

        return {
            "mean": average,
            "median": median,
            "std": std,
            "min": minimum,
            "max": maximum}


    def visualize_run(self, run_uuid: str, results_dir="results"):
        """
        Visualizes the results of a specific test run by reading the corresponding JSON file and plotting the data.
        :param run_uuid: The UUID of the test run to visualize
        :type run_uuid: str
        :param results_dir: The directory where the result JSON files are stored
        """

        target_file = None
        for file_name in os.listdir(results_dir):
            if file_name.endswith(".json") and run_uuid in file_name:
                target_file = os.path.join(results_dir, file_name)
                break
 
        if not target_file:
            logger.error(f"No file found for UUID: {run_uuid}")
            raise FileNotFoundError(f"No file found for UUID: {run_uuid}")
 
        with open(target_file, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                logger.error(f"File {target_file} contains invalid JSON")
                raise ValueError(f"File {target_file} contains invalid JSON")
            
        plt.figure(figsize=(10, 6))

        # TODO: Add more colors if you have more than 4 runs, or use a color map.
        colors = ['blue', 'green', 'orange', 'red']
        labels = []

        for i, run in enumerate(data):
            ammeter_type = run['ammeter_type']
            results = run['results']

            x_labels = ['Mean','Median',  'Std', 'Min', 'Max']
            values = [results['mean'], results['median'], results['std'], results['min'], results['max']]

            plt.plot(x_labels, values, marker='o', color=colors[i], label=ammeter_type, linewidth=2, markersize=8)

        plt.title('Measurement Data Histogram', fontsize=16)
        plt.xlabel('Measurement Type', fontsize=12)
        plt.ylabel('Value', fontsize=12)
        plt.legend(title='Ammeter Types', fontsize=10)
        plt.grid(True)

        plt.tight_layout()
        plt.savefig(f'{results_dir}/Measurement_Data_Histogram.png')
        logger.info("Histogram saved as Measurement_Data_Histogram.png")
