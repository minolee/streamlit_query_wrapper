from setuptools import setup, find_packages

setup(
    name="streamlit_query_wrapper",
    version="0.1.0",
    packages=find_packages(include=["streamlit_query_wrapper", "streamlit_query_wrapper.*"]),
    install_requires=["streamlit"],
    python_requires=">=3.10",
    author="Minho Lee",
    author_email="lmh30002@gmail.com",
    url="https://github.com/minolee/streamlit_query_wrapper"
)