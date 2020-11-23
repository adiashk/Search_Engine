from reader import ReadFile
from configuration import ConfigClass
from parser_module import Parse
from indexer import Indexer
from searcher import Searcher
import utils


def run_engine(corpus_path, output_path, stemming, queries, num_docs_to_retrieve):
    """

    :return:
    """
    number_of_documents = 0

    config = ConfigClass(corpus_path)
    r = ReadFile(corpus_path=config.get__corpusPath())
    p = Parse(stemming)
    indexer = Indexer(config)

    # documents_list = r.read_file(file_name='covid19_07-30.snappy.parquet')  # TODO - handel all files ~50 (can do with from multiprocessing.pool import ThreadPool)
    # documents_list = r.read_file(file_name='covid19_07-08.snappy.parquet')
    # documents_list = r.read_file(file_name='covid19_07-09.snappy.parquet')
    # Iterate over every document in the file
    counter = 0
    names = r.get_files_names_in_dir()
    for name in names:
        documents_list = r.read_file(file_name=str(name))
        for idx, document in enumerate(documents_list):
            parsed_document = p.parse_doc(document)  # parse the document
            number_of_documents += 1
            indexer.add_new_doc(parsed_document)  # index the document data

            counter += 1
            if counter >= 500:
                write_buffer(indexer, number_of_documents / counter)
                counter = 0
        print('Finished parsing and indexing. Starting to export files')



    # utils.save_obj(indexer.inverted_idx, "inverted_idx")
    # utils.save_obj(indexer.postingDict, "post/posting")


def load_index():
    print('Load inverted index')
    inverted_index = utils.load_obj("inverted_idx")
    return inverted_index


def search_and_rank_query(query, inverted_index, k, stemming):
    p = Parse(stemming)
    query_as_list = p.parse_sentence(query)
    searcher = Searcher(inverted_index)
    relevant_docs = searcher.relevant_docs_from_posting(query_as_list)
    ranked_docs = searcher.ranker.rank_relevant_doc(relevant_docs)
    return searcher.ranker.retrieve_top_k(ranked_docs, k)


def write_buffer(indexer, write_number):
    # after 500000 docs --> write the postingDict to the Disk

    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
               'u', 'v', 'w', 'x', 'y', 'z', 'num', '#', '@']
    for l in letters:
        utils.save_obj(indexer.postingDict, (l + str(int(write_number))))

    del indexer.postingDict


def main(corpus_path, output_path, stemming, queries, num_docs_to_retrieve):
    run_engine(corpus_path, output_path, stemming, queries, num_docs_to_retrieve)
    query = input("Please enter a query: ")
    k = int(input("Please enter number of docs to retrieve: "))
    inverted_index = load_index()
    for doc_tuple in search_and_rank_query(query, inverted_index, k, stemming):
        print('tweet id: {}, score (unique common words with query): {}'.format(doc_tuple[0], doc_tuple[1]))
