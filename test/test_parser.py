from parser_module import Parse


class TestParser:
    def setup(self):
        pass

    def test_parser(self):
        p = Parse()
        text1 = '@ampalombo I was going to my grandsons baseball games and the dumb F****s made a mask mandatory, are you kidding me'
        assert p.parse_sentence(text=text1) == ['@ampalombo', 'I', 'going', 'grandsons', 'baseball', 'games', 'dumb', 'F****s', 'made', 'mask', 'mandatory', 'kidding', '10,344.5']
        text2 = 'bla bla bla'
        print('end')
