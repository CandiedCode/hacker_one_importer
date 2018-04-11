from setuptools import setup, find_packages

setup(name='hacker_one_importer',
      version='1.0.0',
      description='HackerOne Jira Integration Service',
      author='CandiedCode',
      packages=find_packages(),
      include_package_data=True,
      entry_points={
          'console_scripts': [
              'h1 = hacker_one_importer.importer:cli'
          ]
      },
      install_requires=[
          'botocore==1.9.19',
          'boto3==1.6.19',
          'h1==1.4.2',
          'jira==1.0.14',
          'colorlog==3.1.2',
          'requests==2.10.0',
          'click==6.7',
          'six==1.11.0'
      ],
      setup_requires=['pytest-runner'],
      tests_require=['pytest'],
      extras_require={
        'dev': ['memory_profiler',
                'psutil'],
        'test': ['pytest',
                 'pytest-mock',
                 'pylint'
                 ]
      })
