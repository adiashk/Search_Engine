import search_engine


corpus_path = None
output_path = None
stemming = True
queries = None
num_docs_to_retrieve = None

if __name__ == '__main__':
    search_engine.main(corpus_path, output_path, stemming, queries, num_docs_to_retrieve)
