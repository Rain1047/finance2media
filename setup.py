from setuptools import setup, find_packages

setup(
    name="finance2media",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.21.0",
        "soundfile>=0.10.3",
        "pyaudio>=0.2.11",
        "funasr>=0.8.0",
        "streamlit>=1.32.0",
        "streamlit-webrtc>=0.47.1",
    ],
) 