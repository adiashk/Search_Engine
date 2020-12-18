class ConfigClass:
    def __init__(self, corpus_path):
        self.corpusPath = corpus_path
        self.savedFileMainFolder = ''
        self.saveFilesWithStem = self.savedFileMainFolder + "/WithStem"
        self.saveFilesWithoutStem = self.savedFileMainFolder + "/WithoutStem"
        self.toStem = False

        # print('Project was created successfully..')

    def get__corpusPath(self):
        return self.corpusPath
