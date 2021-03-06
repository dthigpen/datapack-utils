from setuptools import setup, find_packages

from datapack_utils import __version__

setup(
    name='datapack_utils',
    version=__version__,

    url='https://github.com/dthigpen/datapack-utils',
    author='David Thigpen',
    author_email='davidthigs@gmail.com',
    install_requires=['minecraft-data @ git+https://github.com/SpockBotMC/python-minecraft-data'],
    packages=find_packages()
)