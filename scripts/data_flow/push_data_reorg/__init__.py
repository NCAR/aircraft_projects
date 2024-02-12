

class FieldData():

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.handler = logging.FileHandler('/tmp/push_data.log')
        self.formatter = logging.Formatter('%(asctime)s : %(name)s  : %(funcName)s : %(levelname)s : %(message)s')
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)