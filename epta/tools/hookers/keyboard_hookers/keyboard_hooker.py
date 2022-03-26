import keyboard

from epta.core import BaseTool, ConfigDependent


class KeyboardHooker(BaseTool, ConfigDependent):
    def __init__(self, config: 'Config' = None, name: str = 'keyboard_hooker', **kwargs):
        super(KeyboardHooker, self).__init__(config=config, name=name, **kwargs)

        self.working_state = False
        self.active_state = False
        self.exit_state = False

    def set_state(self, state_name: str, state: bool, *args, **kwargs):
        print(f'setting state {state_name} to {state}')
        setattr(self, state_name, state)

    def _add_hotkeys(self):
        keyboard.add_hotkey(self.config.settings.stop_key, self.set_state, args=('working_state', False))
        keyboard.add_hotkey(self.config.settings.start_key, self.set_state, args=('working_state', True))
        keyboard.add_hotkey(self.config.settings.active_key, self.set_state, args=('active_state', True))
        keyboard.add_hotkey(self.config.settings.exit_key, self.set_state, args=('exit_state', True))

    def use(self):
        self._add_hotkeys()
