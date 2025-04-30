from setuptools import setup, find_packages

setup(
    name="autowk",
    version="0.1.5",
    author="ruyi",
    author_email="losenine@163.com",
    description="基于WebKit的Python自动化浏览器框架",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/LoseNine/AutoWK",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "autowk": [
            "autowk/bin/*.*",
        ],
    },
    install_requires=[
        "psutil>=5.9.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires=">=3.7",
)