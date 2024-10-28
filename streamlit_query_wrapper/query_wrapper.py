from __future__ import annotations
import streamlit as st
import hashlib
from typing import Callable, Any
from functools import wraps, partial
import inspect
__all__ = ["wrap", "checkbox", "radio", "selectbox", "multiselect", "slider", "text_input", "number_input", "sharable_link", "sidebar"]

def SHA1(obj):
    return hashlib.sha1(str(obj).encode()).hexdigest()

_QUERY_TABLES = {}

def get_base_url():
    # https://github.com/streamlit/streamlit/issues/798#issuecomment-1647759949
    import urllib.parse
    session = st.runtime.get_instance()._session_mgr.list_active_sessions()[0]
    st_base_url = urllib.parse.urlunparse([session.client.request.protocol, session.client.request.host, "", "", "", ""])
    return st_base_url

def sharable_link():
    result = ""
    for key, value in _QUERY_TABLES.items():
        if isinstance(value, list):
            for item in value:
                result += f"{key}={item}&"
        else:
            result += f"{key}={value}&"
    st.code(get_base_url() + "?" + result.strip("&"))
    # return result.strip("&")

def map_positional_arg_to_keyword_args(module, *args):
    signature = inspect.signature(module)
    params = list(signature.parameters.keys())
    return {params[i]: args[i] for i in range(len(args))}

def load_value_from_query(query: str, hash_table: dict[str, Any]):
    values = st.query_params.get_all(query)
    if query in st.query_params: st.query_params.pop(query)
    return [hash_table.get(value, value) for value in values]

@st.cache_data
def load_hash_table(items: list[Any]):
    return {SHA1(item)[:3]: item for item in items if should_use_hash(item)}

def should_use_hash(value: Any):
    return isinstance(value, str) and (len(value) > 8 or len(value) == 0 or any(x in value for x in "?&=/"))

def translate_default_value(widget, value: list[str], options: list[Any] | None = None):
    match widget:
        case st.checkbox:
            key = "value"
            _value = eval(value[0])
        case st.radio:
            key = "index"
            _value = options.index(value[0]) # type: ignore
        case st.selectbox:
            key = "index"
            _value = options.index(value[0]) # type: ignore
        case st.multiselect:
            key = "default"
            _value = value
        case st.slider:
            key = "value"
            _value = int(value[0])
        case st.text_input:
            key = "value"
            _value = value[0]
        case st.number_input:
            key = "value"
            _value = eval(value[0])
        case _:
            return {}
    return {key: _value}



def wrap(widget: Callable):
    @wraps(widget)
    def inner_widget(*args, query: str | None = None, **kwargs):
        global _QUERY_TABLES
        mapped_kwargs = map_positional_arg_to_keyword_args(widget, *args) | kwargs
        _query = query or mapped_kwargs.get("key", mapped_kwargs.get("label"))
        
        options = mapped_kwargs.get("options", None)
        hash_table = {}
        reverse_hash_table = {}
        if options is not None:
            hash_table = load_hash_table(options)
            reverse_hash_table = {value: key for key, value in hash_table.items()}
        default_value = load_value_from_query(_query, hash_table)
        if default_value:
            mapped = translate_default_value(widget, default_value, options)
            mapped_kwargs |= mapped

        result = widget(**mapped_kwargs)
        query_value = [reverse_hash_table.get(value, value) for value in result] if isinstance(result, list) else reverse_hash_table.get(result, result)
        if options is not None:
            _QUERY_TABLES[_query] = query_value
        else:
            _QUERY_TABLES[_query] = result
        return result
    return inner_widget

checkbox = wrap(st.checkbox)
radio = wrap(widget=st.radio)
selectbox = wrap(st.selectbox)
multiselect = wrap(st.multiselect)
slider = wrap(st.slider)
text_input = wrap(st.text_input)
number_input = wrap(st.number_input)

class sidebar:
    checkbox = wrap(st.sidebar.checkbox)
    radio = wrap(st.sidebar.radio)
    selectbox = wrap(st.sidebar.selectbox)
    multiselect = wrap(st.sidebar.multiselect)
    slider = wrap(st.sidebar.slider)
    text_input = wrap(st.sidebar.text_input)
    number_input = wrap(st.sidebar.number_input)
    sharable_link = partial(sharable_link)