import numpy as np

class MatrixFileIO:
    @staticmethod
    def write_matrix(matrix, filename):
        try:
            with open(filename, 'w') as file:
                for row in matrix:
                    file.write(' '.join(map(str, row)) + '\n')
        except Exception as e:
            print(f"Error occurred while writing matrix to {filename}: {e}")

    @staticmethod
    def read_matrix(filename):
        try:
            with open(filename, 'r') as file:
                lines = file.readlines()
                matrix = []
                for line in lines:
                    matrix.append(list(map(float, line.split())))
            return np.array(matrix)
        except Exception as e:
            print(f"Error occurred while reading matrix from {filename}: {e}")
            return None
