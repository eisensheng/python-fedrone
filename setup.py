# -*- coding: utf-8 -*-
import os
import subprocess
import sys
from glob import glob

from setuptools.command.develop import develop as DevelopBase
from setuptools import setup, find_packages, Extension


class DevelopCommand(DevelopBase):
    def run(self):
        return_value = DevelopBase.run(self)
        if not self.uninstall:
            try:
                import pip

            except ImportError:
                print >>sys.stderr, (u'Don’t forget to install requirements '
                                     u'from devel_requirements.txt')

            else:
                pip.main(['install', '-r', './devel_requirements.txt', ])

        return return_value


def configure():
    c_flags = []
    cc_name = os.path.basename(os.getenv('CC', 'gcc'))
    if cc_name == 'gcc':
        cc_version_str = subprocess.check_output(['gcc',
                                                  '-dumpversion']).strip()
        cc_version = tuple(int(x) for x in cc_version_str.split('.'))

        c_flags.extend(['--std=c99', ])

        if cc_version >= (4, 7, ):
            # switches are guaranteed to exist at
            # gcc 4.7 (or later, hopefully)
            compiler_warnings = ('address', 'aggregate-return', 'all',
                                 'bad-function-cast', 'cast-align',
                                 'cast-qual', 'extra', 'enum-compare',
                                 'init-self', 'inline',
                                 'jump-misses-init', 'logical-op',
                                 'missing-prototypes', 'redundant-decls',
                                 'shadow', 'strict-prototypes', 'switch-enum',
                                 'unused-but-set-parameter',
                                 'unused-but-set-variable', 'unused-function',
                                 'unused-label', 'unused-parameter',
                                 'unused-variable', 'unused-value',
                                 'unused-result', 'write-strings', )
            c_flags.extend('-W%s' % (a, ) for a in compiler_warnings)

    return c_flags


setup(
    cmdclass={'develop': DevelopCommand, },
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
                           extra_compile_args=configure())],
    entry_points = {
        'console_scripts': [
            'fedrone-demo = fedrone.demo.main:main [demo]',
        ],
    }
)
