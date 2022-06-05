from setuptools import setup, find_packages

setup(
    name='google_places_categorizer',
    version='1.0',
    author='Fernanda R Gubert',
    packages=find_packages(include=['src.*']),
    #namespace_packages=['src'], # utilizar se forem criados subpacotes
    install_requires=open('requirements.txt').readlines(),
    zip_safe=False
)
