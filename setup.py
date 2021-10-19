try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

def get_requirements(filename):
    with open(filename) as file:
        return file.readlines()

def main():
    setup(
        name='genesys_sipserver_exporter',
        author='jmurphyau',
        description='Prometheus exporter for Genesys SIP Server',
        url='https://github.com/jmurphyau/genesys_sipserver_exporter',
        version='1.1',
        python_requires='>=3.6.3',
        install_requires=get_requirements('requirements.txt'),
        scripts=['main.py'],
        packages=find_packages(include=['src', 'src.*'])
    )

if __name__ == "__main__":
    main()
