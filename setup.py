from setuptools import setup
import vgame
 
setup(
    name = "vgame",
    version = vgame.__version__,
    keywords = "vgame",
    author = "cilame",
    author_email = "opaquism@hotmail.com",
    url="https://github.com/cilame/vgame",
    license = "MIT",
    description = "",
    long_description = "",
    long_description_content_type="text/markdown",
    classifiers = [
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
    ],

    packages = [
        "vgame",
    ],
    python_requires=">=3.3",
    install_requires=[
       'pygame',
    ],
)