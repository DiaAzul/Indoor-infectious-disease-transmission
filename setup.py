import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="covid-building-infections", # Replace with your own username
    version="0.0.1",
    author="Tanzo Creative Ltd",
    author_email="",
    description="Simulate transmission of respiratory infection in enclosed environments.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DiaAzul/Covid-19-Environment-Risk-Analysis",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
