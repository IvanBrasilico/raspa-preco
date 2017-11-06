from setuptools import find_packages, setup

LONG_DESCRIPTION = ''
try:
    with open('./README.md', 'r') as f:
        LONG_DESCRIPTION = f.read()
except FileNotFoundError:
    pass

setup(
    name='raspapreco',
    description='Pesquisador de preços',
    long_description=LONG_DESCRIPTION,
    version='0.0.1',
    url='https://github.com/IvanBrasilico/raspa-preco',
    license='MIT',
    author='Ivan Brasilico',
    author_email='brasilico.ivan@gmail.com',
    packages=find_packages(),
    install_requires=[
        'bs4',
        'celery',
        'certifi',
        'chardet',
        'flask',
        'flask_cors',
        'flask_restless',
        'flask_sqlalchemy',
        'idna',
        'json-tricks',
        'requests',
        'SQLAlchemy',
        'urllib3'
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    test_suite="tests",
    package_data={
        'raspapreco': ['locale/*'],
    },
    extras_require={
        'dev': [
            'coverage',
            'flake8',
            'isort',
            'pytest',
            'pytest-cov',
            'pytest-mock',
            'requests-mock',
            'Sphinx',
            'testfixtures',
        ],
    },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
        'Topic :: Software Development :: User Interfaces',
        'Topic :: Utilities',
        'Programming Language :: Python :: 3.5',
    ],
)
