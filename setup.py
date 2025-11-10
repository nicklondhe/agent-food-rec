from setuptools import setup, find_packages

setup(
    name="agent-food-rec",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
    ],
    python_requires=">=3.8",
    author="Nick Londhe",
    description="A food recommendation system using web searches and set differences",
    entry_points={
        "console_scripts": [
            "food-rec=food_rec.cli:main",
        ],
    },
)
