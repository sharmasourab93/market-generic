from abc import abstractclassmethod

from trade.utils import SingletonMeta


class OutputGenerics(metaclass=SingletonMeta):

    @abstractclassmethod
    def communicate_data(cls, *args, **kwargs) -> None: ...
