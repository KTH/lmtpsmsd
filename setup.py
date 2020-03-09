import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="lmtpsmsd-abokth", # Replace with your own username
    version="0.0.1",
    author="Alexander Boström",
    author_email="abo@kth.se",
    description="LMTP to SMS gateway",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/KTH/lmtpsmsd",
    packages=['lmtpsmsd', 'lmtpsmsd._private'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    scripts=['bin/lmtpsmsd'],
)
