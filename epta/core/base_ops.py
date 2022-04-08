from typing import Any, List, Union, Tuple, Iterable, Mapping
import math

from epta.core import BaseTool


class Lambda(BaseTool):
    def __init__(self, fnc: callable, name: str = 'Lambda', **kwargs):
        super(Lambda, self).__init__(name=name, **kwargs)
        self._fnc = fnc

    def use(self, *args, **kwargs) -> Any:
        return self._fnc(*args, **kwargs)


class Wrapper(BaseTool):  # TODO: make partial-like?
    def __init__(self, tool: Any, name: str = 'Wrapper', **kwargs):
        super(Wrapper, self).__init__(name=name, **kwargs)
        self.tool = tool

    def use(self, *args, **kwargs):
        return self.tool

    # def update(self, *args, **kwargs):
    #     if isinstance(self.tool, BaseTool):
    #         self.tool.update(*args, **kwargs)


class Variable(Wrapper):
    # easier tool tracing
    def __init__(self, tool: 'BaseTool', name: str = 'Variable', **kwargs):
        super(Variable, self).__init__(name=name, tool=tool, **kwargs)

    def use(self, *args, **kwargs):
        return self.tool(*args, **kwargs)

    def update(self, *args, **kwargs):
        if isinstance(self.tool, BaseTool):
            self.tool.update(*args, **kwargs)


class Atomic(BaseTool):
    # single dependence
    def __init__(self, key: Union[slice, int, str, Tuple], name: str = 'Atomic', **kwargs):
        super(Atomic, self).__init__(name=name, **kwargs)
        self.key = key

    def use(self, data: Mapping, **kwargs) -> Any:
        return data[self.key]


class SoftAtomic(Atomic):
    # converts dict to flat value
    def __init__(self, *args, name: str = 'SoftAtomic', default_value: Any = None, **kwargs):
        super(SoftAtomic, self).__init__(*args, name=name, **kwargs)
        self._default_value = default_value
        if callable(default_value):
            self._default_value_getter = lambda: default_value()
        else:
            self._default_value_getter = lambda: default_value

    def use(self, data: dict, default_value=None, **kwargs):
        default_value = default_value or self._default_value_getter()
        inp = data.get(self.key, default_value)
        return inp


class Sequential(BaseTool):
    # Do not use sequential with kwargs, as it does not pass them to the tools.
    def __init__(self, tools: List['BaseTool'] = None, name: str = 'Sequential', **kwargs):
        super(Sequential, self).__init__(name=name, **kwargs)
        if tools is None:
            tools = list()

        self.tools = tools

    def use(self, inp: Any = None, **kwargs) -> Any:
        for tool in self.tools:
            inp = tool(inp)
        return inp

    def update(self, *args, **kwargs):
        for tool in self.tools:
            tool.update(*args, **kwargs)

    def append(self, tool: 'BaseTool'):
        if isinstance(tool, BaseTool):
            self.tools.append(tool)


class Product(Sequential):
    def __init__(self, tools: List['BaseTool'] = None, name: str = 'Product', **kwargs):
        super(Product, self).__init__(name=name, tools=tools, **kwargs)

    def use(self, *args, **kwargs):
        result = list()
        for tool in self.tools:
            local_res = tool(*args, **kwargs)
            result.append(local_res)
        return math.prod(result)


class Sum(Sequential):
    def __init__(self, tools: List['BaseTool'] = None, name: str = 'Sum', **kwargs):
        super(Sum, self).__init__(name=name, tools=tools, **kwargs)

    def use(self, *args, **kwargs):
        result = list()
        for tool in self.tools:
            local_res = tool(*args, **kwargs)
            result.append(local_res)
        return sum(result)


class Compose(BaseTool):
    # lambda with tools' tracing
    def __init__(self, fnc: Union['BaseTool', callable], func_args: Tuple[Any, ...] = None,
                 func_kwargs: dict = None, name='Compose', **kwargs):
        super(Compose, self).__init__(name=name, **kwargs)
        self._fnc = fnc

        if func_args is None:
            func_args = tuple()
        self.func_args = func_args

        if func_kwargs is None:
            func_kwargs = dict()
        self.func_kwargs = func_kwargs

        self._tools = list()
        if isinstance(fnc, BaseTool):
            self._tools.append(fnc)

        for arg in self.func_args:
            if isinstance(arg, BaseTool):
                self._tools.append(arg)

        for kwarg in self.func_kwargs.values():
            if isinstance(kwarg, BaseTool):
                self._tools.append(kwarg)

    def _use_args(self, *args, **kwargs) -> tuple:
        func_args = tuple(arg(*args, **kwargs) if isinstance(arg, BaseTool) else arg for arg in
                          self.func_args)
        return func_args

    def _use_kwargs(self, *args, **kwargs) -> dict:
        func_kwargs = {}
        for key, value in self.func_kwargs.items():
            if isinstance(value, BaseTool):
                new_value = value(*args, **kwargs)
            else:
                new_value = value
            func_kwargs[key] = new_value

        return func_kwargs

    def update(self, *args, **kwargs):
        for tool in self._tools:
            tool.update(*args, **kwargs)

    def use(self, *args, **kwargs) -> Any:
        func_args = self._use_args(*args, **kwargs)
        func_kwargs = self._use_kwargs()
        return self._fnc(*func_args, **func_kwargs)


class Parallel(Wrapper):
    # single tool for multiple inputs -> multiple outputs
    def __init__(self, tool: 'BaseTool', name: str = 'Parallel', **kwargs):
        super(Parallel, self).__init__(tool=tool, name=name, **kwargs)

    def use(self, data: Iterable, **kwargs):
        result = list()
        for d in data:
            result.append(self.tool.use(d, **kwargs))
        return result


class Concatenate(Sequential):
    def __init__(self, tools: List['BaseTool'] = None, name: str = 'Concatenate', **kwargs):
        super(Concatenate, self).__init__(name=name, tools=tools, **kwargs)

    def use(self, *args, **kwargs):
        result = list()
        for tool in self.tools:
            result.append(tool(*args, **kwargs))
        return result

    def update(self, *args, **kwargs):
        for tool in self.tools:
            tool.update(*args, **kwargs)


class DataGather(BaseTool):
    # dict to dict data transfer
    def __init__(self, keys: Union[List[Union[tuple, str]], Union[tuple, str]] = None, name='DataGatherer', **kwargs):
        super(DataGather, self).__init__(name=name, **kwargs)
        if keys is None:
            keys = list()
        if isinstance(keys, tuple) or isinstance(keys, str):
            keys = [keys]
        self.keys = keys

    def gather_data(self, data: dict, **kwargs):
        keys = kwargs.get("keys", self.keys)
        return {key: data.get(key) for key in keys}

    def use(self, data: dict, **kwargs) -> dict:
        return self.gather_data(data, **kwargs)


class DataReduce(BaseTool):
    # dict to tuple
    def __init__(self, keys: Union[List[Union[tuple, str]], Union[tuple, str]] = None, name='DataReduce', **kwargs):
        super(DataReduce, self).__init__(name=name, **kwargs)
        if keys is None:
            keys = list()
        if isinstance(keys, tuple) or isinstance(keys, str):
            keys = [keys]
        self.keys = keys

    def reduce_data(self, data: dict, **kwargs):
        keys = kwargs.get("keys", self.keys)
        return tuple(data.get(key) for key in keys)

    def use(self, data: dict, **kwargs) -> tuple:
        return self.reduce_data(data, **kwargs)


class DataSpread(BaseTool):
    # tuple to dict data transfer
    def __init__(self, keys: Union[List[Union[tuple, str]], Union[tuple, str]] = None, name='DataSpreader', **kwargs):
        super(DataSpread, self).__init__(name=name, **kwargs)
        if keys is None:
            keys = list()
        if isinstance(keys, tuple) or isinstance(keys, str):
            keys = [keys]
        self.keys = keys

    def spread_data(self, args: tuple, **kwargs):
        keys = kwargs.get("keys", self.keys)
        return dict(zip(keys, args))

    def use(self, *args, **kwargs) -> dict:
        return self.spread_data(*args)


class DataMergeDict(BaseTool):
    # merge dicts: {**a, **b}
    def __init__(self, name='DataMergeDict', **kwargs):
        super(DataMergeDict, self).__init__(name=name, **kwargs)

    @staticmethod
    def merge_data(args: tuple, **kwargs):
        result = dict()
        for arg in args:
            result.update(arg)
        return result

    def use(self, *args, **kwargs) -> dict:
        return self.merge_data(*args)


class DataMergeList(BaseTool):
    # merge lists: [*a, *b]
    def __init__(self, name='DataMergeList', **kwargs):
        super(DataMergeList, self).__init__(name=name, **kwargs)

    @staticmethod
    def merge_data(args: tuple, **kwargs):
        result = list()
        for arg in args:
            result.append(arg)
        return result

    def use(self, *args, **kwargs) -> list:
        return self.merge_data(*args)


class InputUnpack(BaseTool):
    # use tool(*inp)
    def __init__(self, tool: 'BaseTool', name: str = 'DataUnpack', **kwargs):
        super(InputUnpack, self).__init__(name=name, **kwargs)
        self.tool = tool

    def update(self, *args, **kwargs):
        self.tool.update(*args, **kwargs)

    def use(self, inp: tuple, **kwargs) -> Any:
        return self.tool(*inp, **kwargs)


class Debug(BaseTool):
    def use(self, *args, **kwargs):
        result = tuple(*args)
        return result
