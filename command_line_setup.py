
# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
import os
from os import path
#import glob
# Get list of programs to alias
from programs_list import programs_list

version_num = '0.8.10'
here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()


def do_walk(data_path):
    """
    Walk through data_files and list all in dict format
    """
    data_files = {}
    def cond(File, prefix):
        """
        Return True for useful files
        Return False for non-useful files
        """
        file_path = path.join(prefix, 'data_files', File)
        return (not File.startswith('!') and
                not File.endswith('~') and
                not File.endswith('#') and
                not File.endswith('.pyc') and
                not File.startswith('.') and
                path.exists(path.join(prefix, File)))

    for (dir_path, dirs, files) in os.walk(data_path):
        data_files[dir_path] = [f for f in files if cond(f, dir_path)]
        if not dirs:
            continue
        else:
            for Dir in dirs:
                do_walk(os.path.join(dir_path, Dir))
    return data_files

def parse_dict(dictionary):
    formatted = []
    formatted_dict = {}
    for key in dictionary.keys():
        files = dictionary.pop(key)
        formatted_files = [path.join(key, f) for f in files]
        ind = key.index('/data_files') + len('/data_files/')
        new_key = key[ind:]
        new_key = os.path.join('pmagpy_data_files', new_key)
        formatted.append((new_key, formatted_files))
        formatted_dict[new_key] = formatted_files
    return formatted, formatted_dict

# get formatted list of data_files for setup()
data_files = do_walk(path.join(here, 'data_files'))
formatted, formatted_dict = parse_dict(data_files)


setup(
    name='pmagpy-cli',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=version_num,

    description='Analysis tools for paleo/rock magnetic data',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/PmagPy/PmagPy',

    # Author details
    author='PmagPy team',
    author_email='ltauxe@ucsd.edu',

    # Choose your license
    license='BSD-3',

    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',
        
        # Indicate who your project is intended for
        #'Intended Audience :: Geologists',
        
        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',
        
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],

    keywords='geology paleomagnetism',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['pmagpy', 'pmagpy_tests.examples'
                                    'SPD']), # tests


    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=['numpy', 'matplotlib', 'scripttest'],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    #extras_require={
    #            'dev': ['check-manifest'],
    #            'test': ['coverage'],
    #        },

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    include_package_data=True,
    #package_data={
    #            'images': glob.glob('images/*'),
    #        },
    #package_data=formatted_dict,

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    #data_files=[('pmag_data_files', glob.glob('data_files/*/*.*'))],
    data_files=formatted,


            #data_files=[('bitmaps', ['bm/b1.gif', 'bm/b2.gif']),
            #                              ('config', ['cfg/data.cfg']),
            #                              ('/etc/init.d', ['init-script'])]
            # )
    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    #entry_points={
    #            #'console_scripts': [
    #            #                'angle=programs.angle:main',
    #            #                'angle2.py=programs.angle:main',
    #            #            ],
    #            'console_scripts': programs_list
    #        },
    entry_points={
            'console_scripts': programs_list,
            'gui_scripts': [
                    'magic_gui.py = programs.magic_gui:main',
                    'pmag_gui.py = programs.pmag_gui:main',
                    'demag_gui.py = programs.demag_gui:main',
                    'thellier_gui.py = programs.thellier_gui:main'
            ]
    }

)
