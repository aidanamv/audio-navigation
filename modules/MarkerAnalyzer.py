import numpy as np


class MarkerAnalyzer:

    def __init__(self) -> None:
        self.data = dict()
        pass

    def add_data(self, name: str, res: np.ndarray) -> None:
        y = name
        if name in self.data:
            self.data[name].append(res)
        else:
            self.data[name] = [res]

    def finalize_analyzation(self) -> None:
        stats = ''
        for name, data_array in self.data.items():
            length = len(data_array[0].flatten())
            if length == 1:
                mean = np.mean(data_array)
                stats += f'{name}:\t{mean:.2f}\n'
            elif length == 3:
                mean_1 = np.mean([el[0] for el in data_array])
                mean_2 = np.mean([el[1] for el in data_array])
                mean_3 = np.mean([el[2] for el in data_array])
                
                stats += f'X:\t{mean_1:.2f}\nY:\t{mean_2:.2f}\nZ:\t{mean_3:.2f}\n'
            else:
                raise NotImplementedError
        return stats