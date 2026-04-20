from setuptools import setup, find_packages

setup(
    name="threadwatch",
    version="0.2.0",
    description="Cross-layer pipeline vigilance for the Thread Suite.",
    author="Eugene Dayne Mawuli",
    py_modules=["threadwatch"],
    install_requires=["httpx"],
    python_requires=">=3.8",
)