from setuptools import setup
from simplebackup import __version__

def readme():
    with open('README.md', 'r') as fo:
        return fo.read()

setup(
    name='simple-backup',
    version=__version__,
    python_requires='>=3.8',
    description='a simplebackup program to create full backups using a CLI or GUI',
    long_description=readme(),
    long_description_content_type="text/markdown",
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Environment :: Console',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: System :: Archiving :: Backup',
    ],
    keywords=['python', 'backup', 'fullbackup', 'GUI', 'CLI'],
    url='http://github.com/enchant97/python-simplebackup',
    author='Leo Spratt',
    author_email='contact@enchantedcode.co.uk',
    license='GPLv3',
    packages=['simplebackup'],
    include_package_data=True,
    zip_safe=False
    )
