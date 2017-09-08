
import pandas as pd


def add_unqdetecid(input_file, encoding='utf-8-sig'):
    """
    Adds the unqdetecid column to an input csv file. The resulting file is returned as a pandas DataFrame object.
    
    :param input_file: Path to the input csv file.
    :param encoding: source encoding for the input file (Default utf8-bom)
    :return: padnas DataFrame including unqdetecid column.
    """

    input_df = pd.read_csv(input_file, encoding=encoding)

    input_df[u'unqdetecid'] = input_df.index+1
    input_df = input_df[[u'unqdetecid'] + input_df.columns[:-1].tolist()]
    return input_df
