
import pickle

from resonate.att_formatter import create_att_dictionary_format


if __name__ == '__main__':
    dets = "tests/assertion_files/nsbs_2014_short.csv"
    tags = "tests/assertion_files/nsbs_tag_metadata.xls"
    deployments = "tests/assertion_files/hfx_deployments.xlsx"

    att = create_att_dictionary_format(dets,
                                        tags,
                                        deployments)
    with open('tests/assertion_files/att_archive.pkl', 'wb') as f:
        pickle.dump(att, f)