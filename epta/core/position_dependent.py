from typing import Tuple, Union

from .base_ops import Atomic
from epta.core import ToolDict


class PositionDependent(Atomic):
    """
    A class that requires :attr:`position_manager`.
    By default, takes ``(x, y)`` point at :attr:`key` and updating ``inner_position`` to ``(x0, y0, x1, y1)``.
    Usually used to inherit from as not to pass coordinates as ``args`` to tools.

    Args:
        position_manager (:class:`~epta.core.tool.ToolDict`): a mapping tool dictionary.
        key (str): key to lookup in :attr:`position_manager`.
    """

    def __init__(self, position_manager: 'ToolDict', name: str = 'PositionDependent', **kwargs):
        super(PositionDependent, self).__init__(name=name, **kwargs)
        self.position_manager = position_manager

        self.inner_position = None

    def make_single_position(self, key: str = None, *_, **__) -> Tuple[int, int, int, int]:
        # rewrite this if you want to get multiple positions for crops.
        if key is None:
            key = self.key
        positions = self.position_manager.get(key)
        if positions is None:
            return tuple()
        starting_x = positions.get('x', 0)
        starting_y = positions.get('y', 0)

        current_x_start = starting_x
        current_y_start = starting_y

        if w := positions.get('w', None):
            current_x_end = int(current_x_start + w)
        else:
            current_x_end = None
        if h := positions.get('h', None):
            current_y_end = int(current_y_start + h)
        else:
            current_y_end = None

        current_x_start = int(current_x_start)
        current_y_start = int(current_y_start)

        return current_x_start, current_y_start, current_x_end, current_y_end

    def make_inner_position(self, *args, **kwargs) -> Union[Tuple[int, ...], Tuple[tuple]]:
        position = self.make_single_position(*args, **kwargs)
        return position

    def update(self, *args, **kwargs):
        self.inner_position = self.make_inner_position(*args, **kwargs)
