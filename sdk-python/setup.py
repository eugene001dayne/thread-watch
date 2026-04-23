from setuptools import setup

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="threadwatch",
    version="0.6.0",
    description="Cross-layer pipeline vigilance for the Thread Suite.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Eugene Dayne Mawuli",
    py_modules=["threadwatch"],
    install_requires=["httpx"],
    python_requires=">=3.8",
)