"""Setup do pacote tracking-sdk."""

from setuptools import find_packages, setup

setup(
    name='tracking-sdk',
    version='0.1.0',
    description='SDK para captura automática de erros — Error Tracker',
    author='Error Tracker',
    packages=find_packages(),
    python_requires='>=3.8',
    install_requires=[],
    classifiers=[
        'Framework :: Django',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
)
