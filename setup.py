import os
import setuptools

about = {}
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "sagemaker_migration", "__version__.py")) as f:
    exec(f.read(), about)


with open("readme.md", "r") as f:
    readme = f.read()

required_packages = ["sagemaker>=2.92.1", "boto3>=1.24.0"]
extras = {
    "test": [
        "black",
        "coverage",
        "flake8",
        "mock",
        "pydocstyle",
        "pytest",
        "pytest-cov",
        "sagemaker",
        "tox",
    ]
}

setuptools.setup(
    name=about["__title__"],
    description=about["__description__"],
    version=about["__version__"],
    author=about["__author__"],
    author_email=["__author_email__"],
    long_description=readme,
    long_description_content_type="text/markdown",
    url=about["__url__"],
    license=about["__license__"],
    packages=setuptools.find_packages(),
    include_package_data=True,
    python_requires=">=3.6",
    install_requires=required_packages,
    extras_require=extras,
    entry_points={
        "console_scripts": [
            "sagemaker_migration-configure=sagemaker_migration.configure:main",
        ]
    },
    classifiers=[
        "Development Status :: 1 - Beta",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
