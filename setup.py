import setuptools

description = (
    "shareable-lock is a lock that can be shared across Python processes."
)

setuptools.setup(
    name="shareable_lock",
    version="0.1.0",
    url="https://github.com/natibek/shareable-lock/tree/main",
    author="Nathnael Bekele",
    author_email="nwtbekele@gmail.com",
    python_requires=(">=3.12.0"),
    license="Apache 2.0",
    description=description,
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=["src"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
