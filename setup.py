from distutils.core import setup

def filter_requirements(fn):
    with open(fn) as fh:
        filtered_requirements = []
        for line in fh.readlines():
            if line[0] in ['#', ' ', '-']:
                continue
            filtered_requirements.append(line)
    return filtered_requirements

required = filter_requirements('requirements.txt')
required += filter_requirements('requirements-director.txt')

setup(
    name='FlightGear Orchestrator',
    author="Chris Speck",
    version='0.7.0',
    packages=['fgo'],
    package_data={
        'fgo': ['ui/*', 'ui/assets/*']
    },
    data_files=[
        ('./', ['requirements'])
    ],
    license='GNU GPLv3',
    long_description=open('README.md').read(),
    url="https://github.com/cgspeck/fg-orchestrator",
    platforms=["POSIX", "Windows", "MaxOS"],
    entry_points={
        'console_scripts': [
            'fgo = fgo.cli:main',
        ]
    },
    install_requires=required
)