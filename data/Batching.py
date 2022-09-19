import itertools
from tqdm import tqdm
from data.DataProcessor import get_section_tree, get_distance, read_qrels


def get_page_para_data(qrels_path):
    page_parapair_dist = {}
    page_para_label_dict = read_qrels(qrels_path)
    pages = list(page_para_label_dict.keys())
    for i in tqdm(range(len(pages))):
        page = pages[i]
        sections = list(set([page_para_label_dict[page][para] for para in page_para_label_dict[page].keys()]))
        section_tree = get_section_tree(sections)
        paras = list(page_para_label_dict[page].keys())
        page_parapair_dist[page] = {}
        for p1, p2 in itertools.combinations(paras, 2):
            sec1 = page_para_label_dict[page][p1]
            sec2 = page_para_label_dict[page][p2]
            page_parapair_dist[page][(p1, p2)] = get_distance(sec1, sec2, section_tree)
    return page_para_label_dict, page_parapair_dist


