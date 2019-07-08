""" __Doc__ File handle class """
from setuptools import find_packages, setup
from dnsvalidator.lib.core.__version__ import __version__


def dependencies(imported_file):
    """ __Doc__ Handles dependencies """
    with open(imported_file) as file:
        return file.read().splitlines()


with open("README.md") as file:
    num_installed = False
    try:
        import numpy
        num_installed = True
    except ImportError:
        pass
    setup(
        name="DNSValidator",
        license="GPLv3",
        description="Maintains a list of DNS servers useful for brute forcing.",
        long_description=file.read(),
        author="vortexau and codingo",
        version=__version__,
        author_email="",
        url="https://github.com/vortexau/dnsvalidator",
        packages=find_packages(exclude=('tests')),
        package_data={'dnsvalidator': ['*.txt']},
        entry_points={
            'console_scripts': [
                'dnsvalidator = dnsvalidator.dnsvalidator:main'
            ]
        },
        install_requires=dependencies('requirements.txt'),
        setup_requires=['pytest-runner',
                        '' if num_installed else 'numpy==1.12.0'],
        tests_require=dependencies('test-requirements.txt'),
        include_package_data=True)
