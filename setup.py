from setuptools import setup


setup(
    name='juggler',
    setup_requires=['hgdistver'],
    install_requires=[
        'couchdbkit',
        'couchdb-compose',
        'pytest',
    ],
    get_version_from_hg=True,
)
