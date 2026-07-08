from setuptools import find_packages, setup


setup(
    name="football-predictor",
    version="0.1.0",
    description="Portable football odds and score prediction CLI.",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.9",
    extras_require={
        "collectors": ["curl-cffi>=0.7.0", "beautifulsoup4>=4.12.0"],
    },
    entry_points={"console_scripts": ["football=football_predictor.cli:main"]},
)
