import abc

from epta.core import BaseTool


class BaseRecogniser(BaseTool):
    def __init__(self, name: str = 'base_recogniser', **kwargs):
        super(BaseRecogniser, self).__init__(name=name, **kwargs)

    @abc.abstractmethod
    def image_to_data(self, *args, **kwargs) -> str:
        pass

    def use(self, crops: dict, **kwargs) -> dict:
        result = dict()
        for key, value in crops.items():
            image_rec = self.image_to_data(value, **kwargs)
            result[key] = image_rec
        return result
