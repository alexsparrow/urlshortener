from setuptools import setup

setup(name="urlshortener",
      version="0.1",
      author="Alex Sparrow",
      packages=["urlshortener"],
      package_dir={"urlshortener": "src/urlshortener"},
      zip_safe=False)