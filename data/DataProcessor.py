import json
import os
import gzip
from tqdm import tqdm


class Node:
    def __init__(self, data):
        self.value = data
        self.children = []
        self.parent = None

    def __str__(self):
        return self.value

    def __eq__(self, other):
        return isinstance(other, Node) and self.value == other.value


def get_distance(p1_sec, p2_sec, root):
    # d(p1, p2) = d(r, p1) + d(r, p2) - 2*d(r, lca(p1, p2))
    if root is None:
        print('Root not found!')
        return -1
    n1 = _find(root, p1_sec)
    if n1 is None:
        print(p1_sec + ' is not in the section tree')
        return -1
    n2 = _find(root, p2_sec)
    if n2 is None:
        print(p2_sec + ' is not in the section tree')
        return -1
    lca = _get_LCA(root, n1, n2)
    score = _get_root_dist(n1) + _get_root_dist(n2) - 2 * _get_root_dist(lca)
    return score


# The count of / denotes how deep the section resides in the section tree starting from root
def _get_root_dist(sec):
    assert type(sec) == Node
    return sec.value.count('/') * 1.0


def _get_LCA(root, n1, n2):
    if not _is_reachable(root, n1) or not _is_reachable(root, n2):
        return None
    elif root == n1 or root == n2:
        return root
    else:
        children_in_path = 0
        next_child = None
        for n in root.children:
            if _is_reachable(n, n1) or _is_reachable(n, n2):
                children_in_path += 1
                next_child = n
        if children_in_path == 2:
            return root
        else:
            return _get_LCA(next_child, n1, n2)


def get_section_tree(sections_in_page):
    root = Node(sections_in_page[0].split('/')[0])
    for s in sections_in_page:
        _insert(root, s)
    return root


# root and sec can not be None
def _insert(root, sec):
    if '/' not in sec:
        n = Node(root.value + '/' + sec)
        if n not in root.children:
            root.children.append(n)
            n.parent = root
    else:
        curr_sec = sec.split('/')[0]
        rest_of_sec = '/'.join(sec.split('/')[1:])
        n = Node(root.value + '/' + curr_sec)
        curr_sec_node = None
        for c in root.children:
            if n == c:
                curr_sec_node = c
        if curr_sec_node is None:
            curr_sec_node = n
            root.children.append(curr_sec_node)
            curr_sec_node.parent = root
        _insert(curr_sec_node, rest_of_sec)


def _find(root, sec):
    if sec == '':
        return root
    else:
        curr_sec = sec.split('/')[0]
        rest_of_sec = '/'.join(sec.split('/')[1:])
        for n in root.children:
            if n.value == root.value + '/' + curr_sec:
                return _find(n, rest_of_sec)
    return None


def _is_reachable(root, node):
    if root == node:
        return True
    for n in root.children:
        if _is_reachable(n, node):
            return True
    return False



def print_nodes(r):
    print(r)
    for n in r.children:
        print_nodes(n)


def read_qrels(qrels_path):
    with open(qrels_path, 'r') as f:
        page_para_label_dict = {}
        for l in f:
            label = l.split(' ')[0]
            page = label.split('/')[0]
            para = l.split(' ')[2]
            if page not in page_para_label_dict.keys():
                page_para_label_dict[page] = {para: label}
            else:
                page_para_label_dict[page][para] = label
    return page_para_label_dict


def read_plaintext_passages_from_wikimark_paragraph_corpus(path_to_wikimark_paragraph_corpus_jsonl_splits, qrels_path):
    passage_plaintext_dict = {}
    page_para_label_dict = read_qrels(qrels_path)
    paras = set()
    for page in page_para_label_dict.keys():
        for para in page_para_label_dict[page].keys():
            paras.add(para)
    split_file_list = os.listdir(path_to_wikimark_paragraph_corpus_jsonl_splits)
    for i in tqdm(range(len(split_file_list))):
        fpath = split_file_list[i]
        with gzip.open(os.path.join(path_to_wikimark_paragraph_corpus_jsonl_splits, fpath), mode='rt', encoding='utf-8') as f:
            for l in f:
                para_obj = json.loads(l)
                pid = para_obj['para_id']
                if pid in paras:
                    ptext = ' '.join([para_fragment['text'] for para_fragment in para_obj['para_body']])
                    passage_plaintext_dict[pid] = ptext
    return passage_plaintext_dict


def main():
    q = "D:\\wikimarks_data\\en-wiki-01012022\\benchmarks\\good-articles\\good-articles.train\\train.pages.cbor-hierarchical.qrels"
    sections = {}
    with open(q, 'r') as f:
        for l in f:
            s = l.split(' ')[0]
            p = s.split('/')[0]
            if p in sections.keys():
                sections[p].add(s)
            else:
                sections[p] = {s}
    r = get_section_tree(list(sections['enwiki:Panic%20Room']))
    print_nodes(r)

    sec1 = 'enwiki:Panic%20Room/gublu'
    sec2 = 'enwiki:Panic%20Room/Analysis'
    lca_node = _get_LCA(r, _find(r, sec1), _find(r, sec2))
    print('LCA of ' + sec1 + ' and ' + sec2 + ' is ' + str(lca_node))
    print('Their distance is: %f' % get_distance(sec1, sec2, r))



if __name__ == '__main__':
    main()