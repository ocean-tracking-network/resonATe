
import pandas as pd


def add_unqdetecid(input_file, encoding='utf-8-sig'):
    """Adds the unqdetecid column to an input csv file. The resulting file is returned as a pandas DataFrame object.


    Args:
        input_file (pd.DataFrame|str): Dataframe or path to csv file
        encoding (str, optional): source encoding for the input file. Defaults to 'utf-8-sig'.

    Returns:
        pd.DataFrame: Pandas DataFrame including unqdetecid column.
    """
    if isinstance(input_file, pd.DataFrame):
        input_df = input_file
        input_df['unqdetecid'] = input_df.index + 1
    else:
        input_df = pd.read_csv(input_file, encoding=encoding)
        input_df['unqdetecid'] = input_df.index + 1
    return input_df
