from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="Dpowers",
    version="0.0.2",
    packages=find_packages("Dlib"),
    package_dir={"": "Dlib"},

	#package_data={
        # If any package contains *.json files, include them:
     #   "": ["Dlib/Dhelpers/KeyboardLayouts/layouts_imported_from_xkb/*",
      #      "Dlib/Dpowers/iconpower/icons"]},
    include_package_data=True,
	
    install_requires=["pynput>=1.6.8", "pystray>=0.15",
        "evdev==0.7"],
    
    python_requires=">=3.6",

    # metadata to display on PyPI
    author="DPS",
    author_email="dps@my.mail.de",
    url="https://github.com/dp0s/Dpowers",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)"
    ],
    
    description="Unified Interface for automatic interaction",
    long_description=long_description,
    long_description_content_type="text/markdown"

    # could also include long_description, download_url, etc.
)
