from setuptools import find_packages, setup
setup(
    name='vttmisc',
    packages=find_packages(include=['src']),
    package_dir={'': 'src'},
    version='0.1.0',
    description='A collection of scripts for working with VTT',
    author='Aaron Bell',
    license='MIT',
    install_requires=['fonttools[ufo]>=4.0.0'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest==6.1.0'],
    test_suite='tests',
)