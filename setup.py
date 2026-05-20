from setuptools import setup, find_packages

setup(
    name='frog_package',
    version='1.0',
    description='POS and database management system (customers, inventory) for a retail store.',
    url='https://github.com/admJvsc/projekt-zabka-sklep',
    author='@admJvsc, @Kacperocik, @4PZ',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'PySide6',
        'qfluentwidgets',
        'pandas',
        'openpyxl'
    ],
    zip_safe=False
)