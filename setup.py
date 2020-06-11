import setuptools


setuptools.setup(
    name='sergeant',
    version='0.14.1',
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
    ],
    keywords='tasks worker queue redis async',
    python_requires='>=3.7',
    zip_safe=False,
    install_requires=[
        'hiredis',
        'msgpack',
        'orjson',
        'psutil',
        'pymongo',
        'redis',
    ],
    tests_require=[],
    package_data={},
    packages=setuptools.find_packages(),
)
