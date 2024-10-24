from sc_kpm import ScModule
from .ClassificationAgent import ClassificationAgent


class MessageClassificationModule(ScModule):
    def __init__(self):
        super().__init__(ClassificationAgent())
