from typing import Dict, Iterator, ItemsView, Iterable, Union, List, Sequence, Any

from epta.core import Tool


class ToolDict(Tool):
    """
    Holds tools in a dictionary.

    Args:
        tools (dict, list): dictionary mapping of names to tools or a list.
            If list is passed - keys are tool.name.
    Keyword Args:
        use_behaviour (str): One of 'sequential', 'concatenate', 'dict' to specify ``use`` behaviour.
    """

    def __init__(self,
                 tools: Union[Dict[str, Tool], List[Tool]] = None,
                 name='ToolDict',
                 use_behaviour: str = 'dict',
                 **kwargs) -> None:
        super(ToolDict, self).__init__(name=name, **kwargs)
        if tools is None:
            tools = dict()
        if isinstance(tools, list):
            tools = {tool.name: tool for tool in tools}
        self._tools = tools
        self._use_behaviour = use_behaviour

        # TODO: metaclass?
        __use_mapping = {
            'dict': self.__dict_use,
            'sequential': self.__sequential_use,
            'concatenate': self.__concatenate_use,
        }
        self.use = __use_mapping.get(use_behaviour, self.__dict_use)

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

    @property
    def tools(self) -> Sequence[Tool]:
        return list(self._tools.values())

    def update(self, *args, **kwargs):
        for tool in self.tools:
            if isinstance(tool, Tool):
                tool.update(*args, **kwargs)

    def __sequential_use(self, *args, **kwargs) -> Any:
        # kwargs are passed via key or are common for all tools.

        tools = list(self.items())

        if not tools:
            return None

        key, tool = tools[0]
        inp = tool(*args, **kwargs.get(key, kwargs))
        for key, tool in tools[1:]:
            inp = tool(inp, **kwargs.get(key, kwargs))
        return inp

    def __concatenate_use(self, *args, **kwargs) -> List:
        result = list()
        for tool in self.tools:
            result.append(tool(*args, **kwargs))
        return result

    def __dict_use(self, *args, **kwargs) -> dict:
        data = dict()
        for key, tool in self.items():
            data[key] = tool(*args, **kwargs)
        return data
