import os
import pandas as pd
from os import listdir
from os.path import isfile, join

class ReadFile:
    def __init__(self, corpus_path):
        self.corpus_path = corpus_path

    def read_file(self, file_name):
        """
        This function is reading a parquet file contains several tweets
        The file location is given as a string as an input to this function.
        :param file_name: string - indicates the path to the file we wish to read.
        :return: a dataframe contains tweets.
        """
        full_path = os.path.join(self.corpus_path, file_name)
        df = pd.read_parquet(full_path, engine="pyarrow")
        return df.values.tolist()

    def get_files_names_in_dir(self):
        subdirectories = [x[0] for x in os.walk(self.corpus_path)]
        all_files = []
        for dir in subdirectories:
            # files = [f for f in listdir(self.corpus_path) if isfile(join(self.corpus_path, f))]
            files = [dir+'\\'+f for f in listdir(dir) if isfile(join(dir, f)) and f.endswith(".parquet")]
            all_files.extend(files)

        return all_files


# from dataclasses import dataclass
#
#
# @dataclass
# class doc:
#     a = 1
#     b = None
#     c = None