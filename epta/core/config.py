import abc
from typing import Union
from .settings import Settings


class Config(abc.ABC):
    def __init__(self, settings: Union[Settings, dict] = None, **kwargs):
        super().__init__(**kwargs)
        self.settings = settings or Settings()

    def from_dict(self, data: dict):
        for key, val in data.items():
            setattr(self, key, val)

    def get(self, key: str, default_value=None):
        return getattr(self, key, default_value)


class UpdateDependent(abc.ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # update on config change for example
    def update(self, *args, **kwargs):
        pass


class ConfigDependent(abc.ABC):
    def __init__(self, config: Config, **kwargs):
        super().__init__(**kwargs)
        self.config = config
