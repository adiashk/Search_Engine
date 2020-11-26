import search_engine


corpus_path = "C:\\Users\\Yuval Mor Yosef\\Desktop\\יובל מור יוסף\\בן גוריון\\סמסטר ה\\אחזור\\Data"
# corpus_path = "C:\\Users\\Yuval Mor Yosef\\Desktop\\files"
output_path = None
stemming = False
queries = 'queries.txt'
num_docs_to_retrieve = 5

if __name__ == '__main__':
    search_engine.main(corpus_path, output_path, stemming, queries, num_docs_to_retrieve)
