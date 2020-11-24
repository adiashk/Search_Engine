import gensim
import gzip
import shutil


class Word2vec:
    def __init__(self):
        pass

    # def open_file(self):
    #     # with gzip.open('C:\\Users\\ASUS\\Desktop\\GoogleNews-vectors-negative300.bin.gz') as f_in:
    #     #     with open('GoogleNews-vectors-negative300.bin', 'wb') as f_out:
    #     #         shutil.copyfileobj(f_in, f_out)


    def get_most_similar_words(self, words_list, k):
        model = gensim.models.KeyedVectors.load_word2vec_format('GoogleNews-vectors-negative300.bin', binary=True)

        # dog = model['dog']
        # print(dog.shape)
        # print(dog[:10])

        # result = model.most_similar(positive=['woman', 'king'], negative=['man'], topn=1)
        query_words = []
        for word in words_list:
            if word in model.wv.vocab:
                query_words.append(word)

        result = model.most_similar(positive=query_words, topn=k)
        # result = model.most_similar(positive=words_list, topn=k)
        print(result)
        return result


# word2vec = Word2vec()
# word2vec.get_most_similar_words(['woman', '2'], 3)