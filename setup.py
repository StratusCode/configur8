import io
import re

from setuptools import find_packages, setup


with io.open("README.md", "rt", encoding="utf8") as f:
    readme = f.read()

with io.open("src/configur8/__about__.py", "rt", encoding="utf8") as f:
    version_info = re.search(r"version_info = \((.*)\)", f.read())
    version_info = [x.strip() for x in version_info.group(1).split(",")]
    version = '.'.join(map(str, version_info))


setup_args = dict(
    name="configur8",
    version=version,
    url="https://github.com/StratusCode/configur8",
    maintainer="Nick Joyce",
    maintainer_email="nick@stratuscode.com",
    description=(
        "Python configuration and validation library",
    ),
    long_description=readme,
    packages=find_packages("src"),
    package_dir={"": "src"},
    package_data={"configur8": ["py.typed"]},
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.8",
)

if __name__ == "__main__":
    setup(**setup_args)
