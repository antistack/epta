from typing import Union

from .settings import Settings


class Config:
    def __init__(self, settings: Union[Settings, dict] = None, **kwargs):
        if settings is None:
            settings = dict()
        if isinstance(settings, dict):
            self.settings = Settings.from_dict(settings)
        else:
            self.settings = settings
        super().__init__(**kwargs)

    def from_dict(self, data: dict):
        for key, val in data.items():
            setattr(self, key, val)

    def get(self, key: str, default_value=None):
        return getattr(self, key, default_value)
