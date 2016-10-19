from setuptools import setup


setup(
    name='simeng',
    license='BSD',
    version='0.0.1',
    url='http://github.com/wstlabs/simengine',
    author='wstlabs',
    author_email='notyet@notyet.org',
    description='A simple algorithm for item-based recommendations based on mutual information',
    py_modules=['simeng'],
    install_requires=[],
    packages=['simeng'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
    ],
    entry_points={
        'console_scripts': [
            'simeng = simeng.__main__:main'
        ]
    },
)

