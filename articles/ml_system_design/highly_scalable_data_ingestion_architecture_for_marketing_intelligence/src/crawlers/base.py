import abc


class BaseAbstractCrawler(abc.ABC):

    @abc.abstractmethod
    def extract(self, link: str, **kwargs) -> None: ...