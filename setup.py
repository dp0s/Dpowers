from setuptools import setup, find_packages
import shutil
from time import sleep
import multiprocessing

version_number = "0.0.3c1"


with open("README.md", "r") as fh:
    long_description = fh.read()
    
    


def my_setup(name, **kwargs):
    shutil.rmtree(f"Dlib/{name}.egg-info", ignore_errors=True)
    shutil.rmtree("build", ignore_errors=True)
    print()
    print()
    print(f"------------------------  Package {name} ----------------------------")
    print()
    sleep(1)
    # for creating wheels using bdist_wheel it is somehow necessary to run
    # the setup command inside a seperate process.
    sub_process = multiprocessing.Process(target=setup_process, args=(name,),
            kwargs=kwargs)
    sub_process.start()
    sub_process.join()

def setup_process(name, **kwargs):
    setup(**kwargs,
        name=name,
        packages=find_packages("Dlib", include=[f"{name}*"]),
        package_dir={"": "Dlib"},
        version=version_number,
        include_package_data=False,
        ####must stay disabled to allow package_data option !!!
        python_requires=">=3.6", # metadata to display on PyPI
        author="DPS", author_email="dps@my.mail.de",
        url="https://github.com/dp0s/Dpowers",
        classifiers=["Programming Language :: Python :: 3",
            "License :: OSI Approved :: GNU General Public License v3 (GPLv3)"],
         )





my_setup("Dpowers",
    package_data = {"Dpowers.iconpower.icons" : ["*"]},

    install_requires=["pynput>=1.6.8", "pystray>=0.15", f"Dhelpers=="
                f"{version_number}"],

    description="Unified Interface for automatic interaction",
    long_description=long_description,
    long_description_content_type="text/markdown"
        )



my_setup("Dhelpers",
        package_data = {"Dhelpers.KeyboardLayouts.layouts_imported_from_xkb"
        : ["*"]},
        install_requires=["evdev==1.2.0", "psutil>=5.4.2"],
        description="Dhelpers support modules"
        )