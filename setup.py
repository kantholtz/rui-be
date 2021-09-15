from setuptools import setup

setup(
    name='rui-be',
    version='0.8.0',

    install_requires=[
        'Flask~=2.0.1'
    ],

    extras_require={
        'dev': [
            'pytest'
        ]
    }
)
