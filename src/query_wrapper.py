from __future__ import annotations
import streamlit as st
import hashlib
from typing import Callable, Any
from functools import wraps, partial
import inspect
__all__ = ["checkbox", "radio", "selectbox", "multiselect", "slider", "text_input", "number_input"]

def SHA1(obj):
    return hashlib.sha1(str(obj).encode()).hexdigest()

# 1) QueryWrapper(st.xxx("asdf", ...), query="") -> 불가능
# 2) QueryWrapper(st.xxx, )
# 3) QueryWrapper(st.xxx)(xxx)
# 4) stq.radio(xxx) -> 제일 무난한듯?

_QUERY_TABLES = {}

def load_value_from_query(query: str):
    values = st.query_params.get_all(query)
    if query in st.query_params: st.query_params.pop(query)
    return values

@st.cache_data
def load_hash_table(items: list[Any]):
    return {SHA1(item): item for item in items}

def should_use_hash(value: Any):
    return isinstance(value, str) and len(value) > 8

def load_options(widget, *args, **kwargs):
    match widget:
        case st.radio:
            return args[1] if len(args) > 1 else kwargs["options"],
        case st.selectbox:
            return args[1] if len(args) > 1 else kwargs["options"],
        case st.multiselect:
            return args[1] if len(args) > 1 else kwargs["options"],

def set_default_value(widget, value: list[str]):
    key = None
    match widget:
        case st.checkbox:
            key = "value"
            value = eval(value[0])
        case st.radio:
            key = "index"
        case st.selectbox:
            key = "value"
        case st.multiselect:
            key = "default"
        case st.slider:
            key = "value"
        case st.text_input:
            key = "value"
        case st.number_input:
            key = "value"


def wrap(widget, *, query: str | None = None, option_key: str | None = None, default_key: str | None = None):
    key = inspect.signature(widget).parameters.get("key")
    @wraps(widget.__call__)
    def inner_widget(*args, **kwargs):
        
        items = load_options(widget, *args, **kwargs)
        default_value = load_value_from_query(query)
        hash_table = load_hash_table(items)

        return widget(*args, **kwargs)
    return inner_widget

checkbox = partial(wrap, st.checkbox)
radio = partial(wrap, st.radio)
selectbox = partial(wrap, st.selectbox)
multiselect = partial(wrap, st.multiselect)
slider = partial(wrap, st.slider)
text_input = partial(wrap, st.text_input)
number_input = partial(wrap, st.number_input)

