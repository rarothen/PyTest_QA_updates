import matplotlib.pyplot as plt
import statistics


class ResultAnalyzer:
    def __init__(self, data: list[float]):
        if len(data) == 0:
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
    
# Visualization of measurement data
# Performance consistency evaluation

    def visualize_data(self):
        """
        Creates a histogram of the measurement data using matplotlib.        
        """
        plt.hist(self.data, bins=20, alpha=0.7)
        plt.title("Measurement Data Distribution")
        plt.xlabel("Current (A)")
        plt.ylabel("Frequency")
        plt.grid()
        plt.show()
    
    def evaluate_performance_consistency(self):
        # Placeholder for consistency evaluation logic
        # This could involve checking for outliers, trends, or comparing against expected values
        pass
    


