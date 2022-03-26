import abc


class Settings(abc.ABC):
    def update(self, data: dict):
        for key, value in data.items():
            setattr(self, key, value)

    def get_dict(self):
        return self.__dict__

    def get_items(self):
        return self.__dict__.items()

    def get(self, key: str, default_value=None):
        return getattr(self, key, default_value)
