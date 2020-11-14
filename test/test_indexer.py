from reader import ReadFile
from configuration import ConfigClass
from parser_module import Parse
from indexer import Indexer
from searcher import Searcher
import utils



class TestIndexer:
    def setup(self):
        pass

    def test_add_new_doc(self):
        config = ConfigClass()
        r = ReadFile(corpus_path=config.get__corpusPath())
        p = Parse()
        indexer = Indexer(config)
        documents_list = r.read_file(file_name='sample3.parquet')
        # text1 = '@ampalombo I was going to my grandsons baseball games and the dumb F****s made a mask mandatory, are you kidding me'
        assert indexer.add_new_doc()
