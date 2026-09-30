from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="quraysh",
    version="3.0.0",
    author="Mohammed",
    description="لغة برمجة عربية كاملة — مبنية على Lisp",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/arabsincyber/Quraysh",
    packages=find_packages(where="src") + ["qur"],
    package_dir={"": "src", "qur": "tools/qur"},
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "quraysh=quraysh.repl:main",
            "qur=qur.main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: Arabic",
    ],
)
