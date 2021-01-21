import setuptools


setuptools.setup(
    name='sergeant',
    version='0.18.3',
    author='Gal Ben David',
    author_email='gal@intsights.com',
    url='https://github.com/Intsights/sergeant',
    project_urls={
        'Source': 'https://github.com/Intsights/sergeant',
    },
    license='MIT',
    description='Fast, Safe & Simple Asynchronous Task Queues Written In Pure Python',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    keywords='tasks worker queue redis async',
    python_requires='>=3.7',
    zip_safe=False,
    install_requires=[
        'hiredis==1.*',
        'msgpack==1.*',
        'orjson==3.*',
        'psutil==5.*',
        'pymongo==3.*',
        'redis==3.*',
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
    package_data={},
    packages=setuptools.find_packages(),
)
