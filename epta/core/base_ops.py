from typing import Any, List, Union, Tuple, Iterable, Mapping
import math

from epta.core import BaseTool


class Lambda(BaseTool):
    """
    Lambda tool.

    Args:
        fnc (callable, ): object to be called with passed ``*args`` and ``**kwargs``.
    """
    def __init__(self, fnc: callable, name: str = 'Lambda', **kwargs):
        super(Lambda, self).__init__(name=name, **kwargs)
        self._fnc = fnc

    def use(self, *args, **kwargs) -> Any:
        return self._fnc(*args, **kwargs)


class Wrapper(BaseTool):  # TODO: make partial-like?
    """
    Wrapper to pass tools as ``args`` or ``kwargs`` in :class:`~epta.core.base_ops.Compose`.
    ``.update`` method will not be invoked on the wrapped tool.
    """
    def __init__(self, tool: Any, name: str = 'Wrapper', **kwargs):
        super(Wrapper, self).__init__(name=name, **kwargs)
        self.tool = tool

    def use(self, *args, **kwargs):
        return self.tool

    # def update(self, *args, **kwargs):
    #     if isinstance(self.tool, BaseTool):
    #         self.tool.update(*args, **kwargs)


class Variable(Wrapper):
    """
    May be used in future to trace tools graph.

    Args:
        tool (BaseTool): tool to store.
    """
    def __init__(self, tool: 'BaseTool', name: str = 'Variable', **kwargs):
        super(Variable, self).__init__(name=name, tool=tool, **kwargs)

    def use(self, *args, **kwargs):
        return self.tool(*args, **kwargs)

    def update(self, *args, **kwargs):
        if isinstance(self.tool, BaseTool):
            self.tool.update(*args, **kwargs)


class Atomic(BaseTool):
    """
    Get value from the inputs by :attr:`key`.

    Args:
        key (slice, int, str, tuple): key to get.
    """
    def __init__(self, key: Union[slice, int, str, Tuple], name: str = 'Atomic', **kwargs):
        super(Atomic, self).__init__(name=name, **kwargs)
        self.key = key

    def use(self, data: Mapping, **kwargs) -> Any:
        return data[self.key]


class SoftAtomic(Atomic):
    """
    Same as :class:`~epta.core.base_ops.Atomic` but with soft get.

    Keyword Args:
        default_value (Any): `callable` constructor to call or static value to return on every use if :attr:`key`
            was not found in input `data`.
    """
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
    """
    Sequential modules application. Handles ``update`` method.

    Keyword Args:
        tools (list): List of tools to use sequentially.
    """
    def __init__(self, tools: List['BaseTool'] = None, name: str = 'Sequential', **kwargs):
        super(Sequential, self).__init__(name=name, **kwargs)
        if tools is None:
            tools = list()

        self.tools = tools

    def use(self, inp: Any = None, **kwargs) -> Any:
        # kwargs are not passed to the tools
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
    """
    Custom function application with given ``args`` and ``kwargs`` that can be tools or values.
    If some of the arguments are tools - they are also called before passing to the :attr:`fnc` with a given inputs.
    Tools are stored inside on the constructor call. To proper ``update`` handling use unique tool names.

    Args:
        fnc (BaseTool, callable): Tool or function to use.

    Keyword Args:
         func_args (tuple): Tuple of inputs passed to the :attr:`fnc`. Tools to be called on use.
         func_kwargs (dict): Dict of kwargs to the :attr:`fnc`. Tools to be called on use.
    """
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


class Parallel(Variable):
    """
    Apply singe tool for the given inputs.

    Args:
        tool (BaseTool): Tool to use.
    Returns:
        result (list): [:attr:`tool`(inputs), ...]
    """
    def __init__(self, tool: 'BaseTool', name: str = 'Parallel', **kwargs):
        super(Parallel, self).__init__(tool=tool, name=name, **kwargs)

    def use(self, data: Iterable, **kwargs):
        result = list()
        for d in data:
            result.append(self.tool(d, **kwargs))
        return result


class Concatenate(Sequential):
    """
    Apply multiple tools to the single input.

    Keyword Args:
        tools (list): Tools to use.

    Returns:
        result (list): Multiple tools result.
    """
    def __init__(self, tools: List['BaseTool'] = None, name: str = 'Concatenate', **kwargs):
        super(Concatenate, self).__init__(name=name, tools=tools, **kwargs)

    def use(self, *args, **kwargs):
        result = list()
        for tool in self.tools:
            result.append(tool(*args, **kwargs))
        return result


class DataGather(BaseTool):
    """
    Select :attr:`keys` from the input data. dict -> dict.
    Results may be ``None`` if key is not present.

    Keyword Args:
        keys: keys to select on use.
    """
    def __init__(self, keys: Union[List[Union[tuple, str]], Union[tuple, str]] = None, name='DataGatherer', **kwargs):
        super(DataGather, self).__init__(name=name, **kwargs)
        if keys is None:
            keys = list()
        if isinstance(keys, tuple) or isinstance(keys, str):
            keys = [keys]
        self.keys = keys

    def _gather_data(self, data: dict, **kwargs):
        keys = kwargs.get("keys", self.keys)
        return {key: data.get(key) for key in keys}

    def use(self, data: dict, **kwargs) -> dict:
        return self._gather_data(data, **kwargs)


class DataReduce(BaseTool):
    """
    Select :attr:`keys` from the input data. dict -> tuple.
    Results may be ``None`` if key is not present.

    Keyword Args:
        keys: keys to select on use.
    """
    def __init__(self, keys: Union[List[Union[tuple, str]], Union[tuple, str]] = None, name='DataReduce', **kwargs):
        super(DataReduce, self).__init__(name=name, **kwargs)
        if keys is None:
            keys = list()
        if isinstance(keys, tuple) or isinstance(keys, str):
            keys = [keys]
        self.keys = keys

    def _reduce_data(self, data: dict, **kwargs):
        keys = kwargs.get("keys", self.keys)
        return tuple(data.get(key) for key in keys)

    def use(self, data: dict, **kwargs) -> tuple:
        return self._reduce_data(data, **kwargs)


class DataSpread(BaseTool):
    """
    Attach :attr:`keys` to the input data. tuple -> dict.

    Keyword Args:
        keys: keys to attach on use.
    """
    def __init__(self, keys: Union[List[Union[tuple, str]], Union[tuple, str]] = None, name='DataSpreader', **kwargs):
        super(DataSpread, self).__init__(name=name, **kwargs)
        if keys is None:
            keys = list()
        if isinstance(keys, tuple) or isinstance(keys, str):
            keys = [keys]
        self.keys = keys

    def _spread_data(self, args: tuple, **kwargs):
        keys = kwargs.get("keys", self.keys)
        return dict(zip(keys, args))

    def use(self, *args, **kwargs) -> dict:
        return self._spread_data(*args)


class DataMergeDict(BaseTool):
    """
    Merge multiple dictionaries. {**a, **b, ...}.
    """
    def __init__(self, name='DataMergeDict', **kwargs):
        super(DataMergeDict, self).__init__(name=name, **kwargs)

    @staticmethod
    def _merge_data(args: tuple, **kwargs):
        result = dict()
        for arg in args:
            result.update(arg)
        return result

    def use(self, *args, **kwargs) -> dict:
        return self._merge_data(*args)


class DataMergeList(BaseTool):
    """
    Merge multiple lists. [**a, **b, ...].
    """
    def __init__(self, name='DataMergeList', **kwargs):
        super(DataMergeList, self).__init__(name=name, **kwargs)

    @staticmethod
    def _merge_data(args: tuple, **kwargs):
        result = list()
        for arg in args:
            result.append(arg)
        return result

    def use(self, *args, **kwargs) -> list:
        return self._merge_data(*args)


class InputUnpack(Variable):
    """
    Use tool on the unpacked ``tuple`` of ``args``. tool(*inp).

    Args:
        tool (BaseTool): tool to use.
    """
    def __init__(self, tool: 'BaseTool', name: str = 'DataUnpack', **kwargs):
        super(InputUnpack, self).__init__(tool=tool, name=name, **kwargs)

    def use(self, inp: tuple, **kwargs) -> Any:
        return self.tool(*inp, **kwargs)


class Debug(BaseTool):
    # Debug tool
    def use(self, *args, **kwargs):
        result = tuple(*args)
        return result
