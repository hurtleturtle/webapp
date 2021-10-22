from setuptools import setup, find_packages

setup(
    name='wuxia',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
        'werkzeug',
        'pandas',
        'lipsum',
        'bs4',
        'lxml',
        'click',
        'uwsgi',
        'docker',
        'jinja2',
        'mysql-connector-python',
        'cryptography'
    ],
)
