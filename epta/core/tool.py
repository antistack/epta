from typing import Any, Dict, Iterator, ItemsView, Iterable, Union, List

from .meta import UpdateDependent


class Tool(UpdateDependent):
    """
    Base class for tool instance.

    Args:
        name (str): Tool name.
    """

    def __init__(self, name: str = 'Tool', **kwargs):
        super().__init__(**kwargs)
        self.name = name

    def use(self, *args, **kwargs) -> Any:
        pass

    def update(self, *args, **kwargs):
        pass

    def __call__(self, *args, **kwargs):
        return self.use(*args, **kwargs)


class ToolDict(Tool):
    """
    Holds tools in a dictionary.

    Args:
        tools (dict, list): dictionary mapping of names to tools or a list.
            If list is passed - keys are tool.name.
    """

    def __init__(self, tools: Union[Dict[str, Tool], List[Tool]] = None, name='ToolDict', **kwargs) -> None:
        super(ToolDict, self).__init__(name=name, **kwargs)
        if tools is None:
            tools = dict()
        if isinstance(tools, list):
            tools = {tool.name: tool for tool in tools}
        self._tools = tools

    def __getitem__(self, key: str) -> Tool:
        return self._tools[key]

    def __setitem__(self, key: str, tool: Tool) -> None:
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

    def pop(self, key: str) -> Tool:
        v = self[key]
        del self[key]
        return v

    def keys(self) -> Iterable[str]:
        return self._tools.keys()

    def items(self) -> ItemsView[str, Tool]:
        return self._tools.items()

    def values(self) -> Iterable[Tool]:
        return self._tools.values()

    def add_tool(self, key: str, tool: Tool):
        self._tools[key] = tool

    def get(self, key: str, default_value=None):
        return self._tools.get(key, default_value)

    def update(self, *args, **kwargs):
        for tool in self._tools.values():
            if isinstance(tool, Tool):
                tool.update(*args, **kwargs)

    def use(self, *args, **kwargs) -> dict:
        data = dict()
        for tool in self._tools.values():
            data[tool.name] = tool(*args, **kwargs)
        return data
