from distutils.core import setup

packages = [
    "eventsourcing_sqlalchemy",
]

install_requires = [
    "eventsourcing>=9.1.1",
    "sqlalchemy<=1.4.99999,>=1.4.0",
    "sqlalchemy-utils>=0.37.8",
]

setup(
    name="eventsourcing_sqlalchemy",
    version="0.0.1",
    description="Python package for eventsourcing with SQLAlchemy",
    author="John Bywater",
    author_email="john.bywater@appropriatesoftware.net",
    url="https://github.com/pyeventsourcing/eventsourcing-sqlalchemy",
    license="BSD-3-Clause",
    packages=packages,
    package_data={"eventsourcing_sqlalchemy": ["py.typed"]},
    install_requires=install_requires,
)
