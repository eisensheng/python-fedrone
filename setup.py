# -*- coding: utf-8 -*-
import subprocess
import os
from glob import glob
from setuptools import setup, find_packages, Extension


c_flags = []
cc_name = os.path.basename(os.getenv('CC', 'gcc'))
if cc_name == 'gcc':
    cc_version_str = subprocess.check_output(['gcc', '-dumpversion']).strip()
    cc_version = tuple(int(x) for x in cc_version_str.split('.'))

    c_flags.extend(['--std=c99', ])

    if cc_version >= (4, 7, ):
        # switches are guaranteed to exist at gcc 4.7 (or later, hopefully)
        compiler_warnings = ('address', 'aggregate-return', 'all',
                             'bad-function-cast', 'cast-align', 'cast-qual',
                             'extra', 'enum-compare', 'init-self', 'inline',
                             'jump-misses-init', 'logical-op',
                             'missing-prototypes', 'redundant-decls',
                             'shadow', 'strict-prototypes', 'switch-enum',
                             'unused-but-set-parameter',
                             'unused-but-set-variable', 'unused-function',
                             'unused-label', 'unused-parameter',
                             'unused-variable', 'unused-value',
                             'unused-result', 'write-strings', )
        c_flags.extend('-W%s' % (a, ) for a in compiler_warnings)


setup(
    name='FeDrone',
    version='1.1',
    packages=find_packages(),

    extras_require={
        'demo': ['pyglet == 1.2alpha1', ]
    },
    url='https://bitbucket.org/eisensheng/python-fedrone',
    license='MIT',
    author='Arthur S.',
    author_email='eisensheng@gmail.com',
    description='',
    ext_modules=[Extension('fedrone.video._decoder',
                           glob('src/*.c'),
                           extra_compile_args=c_flags)],
    entry_points = {
        'console_scripts': [
            'fedrone-demo = fedrone.demo.main:main [demo]',
        ],
    }
)
