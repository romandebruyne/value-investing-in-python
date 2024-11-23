import pandas as pd
import numpy as np

class CalculationUtils:
    def __init__(self):
        raise NotImplementedError("This class should not be instantiated.")

    @staticmethod
    def calculate_covariance_matrix(series_x, series_y):
        return np.cov(series_x, series_y)

    @staticmethod
    def compute_median(values):
        # If more than 50% of datapoints are NaN, return NaN:
        if pd.isna(values).sum() < len(values) * 0.5:
            return np.nanmedian(values)
        else:
            return np.nan