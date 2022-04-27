import abc

class UpdateDependent(abc.ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @abc.abstractmethod
    def update(self, *args, **kwargs):
        pass


class ConfigDependent:
    def __init__(self, config: 'Config', **kwargs):
        self.config = config
        super().__init__(**kwargs)
