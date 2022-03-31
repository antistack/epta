from typing import Any, Dict, Iterator, ItemsView, Iterable, Union, List

from .config import UpdateDependent

class BaseTool(UpdateDependent):
    def __init__(self, name: str = 'BaseTool', **kwargs):
        super().__init__(**kwargs)
        self.name = name
        # TODO: add _tools for common update method.

    def get(self, key: str, default_value=None):
        return getattr(self, key, default_value)

    def use(self, *args, **kwargs) -> Any:
        pass

    def __call__(self, *args, **kwargs):
        return self.use(*args, **kwargs)


class ToolDict(BaseTool):
    def __init__(self, tools: Union[Dict[str, BaseTool], List[BaseTool]] = None, name='ToolDict', **kwargs) -> None:
        super(ToolDict, self).__init__(name=name, **kwargs)
        if tools is None:
            tools = dict()
        if isinstance(tools, list):
            tools = {tool.name: tool for tool in tools}
        self._tools = tools  # TODO: change to ordered dict and proper add_tool/_update

    def __getitem__(self, key: str) -> BaseTool:
        return self._tools[key]

    def __setitem__(self, key: str, tool: BaseTool) -> None:
        self.add_tool(key, tool)

    def __delitem__(self, key: str) -> None:
        del self._tools[key]

    def __len__(self) -> int:
        return len(self._tools)

    def __iter__(self) -> Iterator[str]:
        return iter(self._tools)

    def __contains__(self, key: str) -> bool:
        return key in self._tools

    def clear(self) -> None:
        self._tools.clear()

    def pop(self, key: str) -> BaseTool:
        v = self[key]
        del self[key]
        return v

    def keys(self) -> Iterable[str]:
        return self._tools.keys()

    def items(self) -> ItemsView[str, BaseTool]:
        return self._tools.items()

    def values(self) -> Iterable[BaseTool]:
        return self._tools.values()

    def add_tool(self, key: str, tool: BaseTool):
        self._tools[key] = tool

    def get(self, key: str, default_value=None):
        return self._tools.get(key, default_value)

    def update(self, *args, **kwargs):
        for tool in self._tools.values():
            tool.update(*args, **kwargs)
