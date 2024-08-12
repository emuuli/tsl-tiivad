from setuptools import setup, find_namespace_packages
exec(open('tiivad/version.py').read())

setup(
    name='tiivad',
    version=__version__,
    license='MIT',
    author="Eerik Muuli",
    author_email='',
    packages=find_namespace_packages(),
    url='https://github.com/emuuli/tsl-tiivad',
    install_requires=[
    ],

)
