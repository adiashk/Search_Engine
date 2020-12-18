import csv
import errno
import os
import pathlib
from collections import defaultdict

from reader import ReadFile
from configuration import ConfigClass
from parser_module import Parse
from indexer import Indexer
from searcher import Searcher
import utils
import time

from word2vec import Word2vec

letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
           'u', 'v', 'w', 'x', 'y', 'z', 'num', '#', '@']


def run_engine(corpus_path, output_path, stemming, queries, num_docs_to_retrieve, word2vec):
    """

    :return:
    """
    # print("start: ", time.asctime(time.localtime(time.time())))
    number_of_documents = 0
    num_of_writes = 1
    config = ConfigClass(corpus_path)
    r = ReadFile(corpus_path=config.get__corpusPath())
    p = Parse(stemming)
    indexer = Indexer(config, word2vec)
    # documents_list = r.read_file(file_name='covid19_07-30.snappy.parquet')  # TODO - handel all files ~50 (can do with from multiprocessing.pool import ThreadPool)

    # Iterate over every document in the file
    counter = 0
    names = r.get_files_names_in_dir()
    for name in names:
        documents_list = r.read_file_by_name(file_name=str(name))
        for idx, document in enumerate(documents_list):
            parsed_document = p.parse_doc(document)  # parse the document
            if parsed_document == {}:  # RT
                continue
            number_of_documents += 1

            indexer.add_new_doc(parsed_document, num_of_writes)  # index the document data
            counter += 1
            if counter >= 500000:
                write_and_clean_buffer(indexer, num_of_writes, stemming,config, output_path)
                counter = 0
                # print("finish parser & index number: ", num_of_writes, " At: ", time.asctime(time.localtime(time.time())))
                num_of_writes += 1
        # print('Finished parsing and indexing. Starting to export files')
    write_and_clean_buffer(indexer, num_of_writes, stemming,config, output_path)
    # print("finish parser & index: ", time.asctime(time.localtime(time.time())))
    indexer.inverted_idx = {key: val for key, val in indexer.inverted_idx.items() if val != 1}
    utils.save_obj(indexer.inverted_idx, "inverted_idx")
    # print("finish save index: ", time.asctime(time.localtime(time.time())))

    return num_of_writes


def write_and_clean_buffer(indexer, write_number, stemming,config, output_path):
    # after 500000 docs --> write the postingDict to the Disk

    # path = pathlib.Path().absolute()
    # path = output_path

    if stemming:
        # save_path = os.path.join(output_path, config.saveFilesWithStem)
        save_path = str(output_path) + config.saveFilesWithStem + "/"
    else:
        # save_path = os.path.join(output_path, config.saveFilesWithoutStem)
        save_path = str(output_path) + config.saveFilesWithoutStem + "/"

    if not os.path.exists(os.path.dirname(save_path)):
        os.makedirs(os.path.dirname(save_path))

    for l in letters:
        filename = str(save_path + l + str(int(write_number)))
        if l == 'num':
            dic_letters = {key: indexer.postingDict[key] for key in indexer.postingDict.keys() if key[0].isdigit()}
        else:
            dic_letters = {key: indexer.postingDict[key] for key in indexer.postingDict.keys() if key[0].lower() == l}
        utils.save_obj(dic_letters, filename)

    indexer.postingDict = {}
    indexer.postingDict = defaultdict(list)

    if stemming:
        save_path = str(output_path) + '\\documents_stem\\'
    else:
        save_path = str(output_path) + '\\documents\\'

    if not os.path.exists(os.path.dirname(save_path)):
        os.makedirs(os.path.dirname(save_path))
    filename = str(save_path + str(int(write_number)))
    utils.save_obj(indexer.documents_dict, filename)

    indexer.documents_dict = {}
    indexer.documents_dict = defaultdict(list)


# def remove_duplicates(documents_dict):
#     # ValueError: The truth value of an array with more than one element is ambiguous. Use a.any() or a.all()
#     temp = []
#     res = dict()
#     for key, val in documents_dict.items():
#         if val not in temp:
#             temp.append(val)
#             res[key] = val
#     return res

def union_posting_files(num_of_writes, stemming,config, output_path):
    # inverted_index = utils.load_obj("inverted_idx")
    # path = pathlib.Path().absolute()
    path = output_path
    if stemming:
        save_path = str(path) + config.saveFilesWithStem + "/"
    else:
        save_path = str(path) + config.saveFilesWithoutStem + "/"
    counter = 1
    for l in letters:
        filename = str(save_path + l + str(counter))
        dict1 = utils.load_obj(filename)
        while counter < num_of_writes:
            counter += 1
            filename = str(save_path + l + str(counter))
            dict2 = utils.load_obj(filename)
            dict1 = union_2_files(dict1, dict2)
        counter = 1
        filename = str(save_path + l)
        dict1 = {k: v for k, v in dict1.items() if len(v) >= 2}
        utils.save_obj(dict1, filename)


# def union_2_files(dict1, dict2):
#     dd = defaultdict(list)
#     for d in (dict1, dict2):
#         for key, value in d.items():
#             dd[key].extend(value)
#     return dd


def union_2_files(dict1, dict2):
    dd = defaultdict(list)
    for d in (dict1, dict2):
        for key, value in d.items():
            if key[0].isupper():  # key is uppercase
                if key.lower() in dd:  # there is uppercase in dict so add value to lower
                    dd[key.lower()].extend(value)
                else:  # add uppercase to dict, there is no lower
                    dd[key].extend(value)
            elif key[0].upper() in dd:  # key is lowercase and there is uppercase in dict
                dd[key] = value  # add new lower key to dict
                if key.capitalize() in dd:  # if lowercase
                    dd[key].extend(dd[key.capitalize()])  # add value capital to lower
                    del dd[key.capitalize()]
                else:  # add value upper to lower
                    dd[key].extend(dd[key.upper()])
                    del dd[key.upper()]
            else:  # new key
                dd[key].extend(value)
    return dd


# def load_index():
#     print('Load inverted index')
#     inverted_index = utils.load_obj("inverted_idx")
#     # inverted_index = {key: val for key, val in inverted_index.items() if val != 1}
#     return inverted_index


def search_and_rank_query(corpus_path, queries_list, inverted_index, num_docs_to_retrieve, stemming, word2vec, output_path):
    config = ConfigClass(corpus_path)
    p = Parse(stemming)
    answers = defaultdict(list)
    for i, q in enumerate(queries_list):
        # print("start query number: ", i + 1)
        query = p.parse_query(q)
        searcher = Searcher(inverted_index, stemming, word2vec)
        relevant_docs = searcher.relevant_docs_from_posting(query, stemming, config, output_path)
        ranked_docs = searcher.ranker.rank_relevant_doc(relevant_docs, query, word2vec, stemming, output_path)
        answers[i] = searcher.ranker.retrieve_top_k(ranked_docs, num_docs_to_retrieve)
        # print("finish query number: ", i + 1)
    return answers


def read_queries(queries):
    # with open(queries) as f:
    with open(queries, encoding="utf8") as f:
        content = f.readlines()
    # you may also want to remove whitespace characters like `\n` at the end of each line
    content = [x.strip() for x in content]
    return content


def main(corpus_path, output_path, stemming, queries, num_docs_to_retrieve):

    config = ConfigClass(corpus_path)
    word2vec = Word2vec()
    num_of_writes = run_engine(corpus_path, output_path, stemming, queries, num_docs_to_retrieve, word2vec)
    union_posting_files(num_of_writes, stemming,config, output_path)
    # print("finish union posting files: ", time.asctime(time.localtime(time.time())))
    if type(queries) != list:
        queries = read_queries(queries)

    inverted_index = utils.load_inverted_index()
    # temp1 = dict(sorted(inverted_index.items(), key=lambda item: item[1].isdigit(), reverse=False))
    # temp2 = dict(sorted(inverted_index.items(), reverse=True))

    rank_query = search_and_rank_query(corpus_path,queries, inverted_index, num_docs_to_retrieve, stemming, word2vec, output_path)
    path = os.path.join(output_path, 'results.csv')
    with open(path, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Query_num", "Tweet_id", "Rank"])
    for i in rank_query:
        for doc_tuple in rank_query[i]:
            print('tweet id: {}, similarity: {}'.format(doc_tuple[0], doc_tuple[1]))
            with open(path, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([i+1, doc_tuple[0], doc_tuple[1]])
