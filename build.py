import os
import sys
import shutil

DIR = os.getcwd()
MODE = None

def clean():
    src = (DIR + '\\src\\')
    for (root, dirs, files) in os.walk(src):
        if ('Win32' in dirs):
            shutil.rmtree(root + '\\Win32')
        if ('x64' in dirs):
            shutil.rmtree(root + '\\x64')

def archive():
    builds = (DIR + '\\.builds\\')
    shutil.make_archive('release', 'zip', builds)
    os.rename(DIR + '\\release.zip', DIR + '\\.builds\\release.zip')

def package(architecture):
    builds = (DIR + '\\.builds\\')
    out = (builds + architecture)

    if os.path.isdir(out):
        shutil.rmtree(out)
    os.mkdir(out)

    for file in os.listdir(builds):
        if file.endswith('.pdb') and (MODE != 'debug'):
            os.remove(builds + file)
        elif file.endswith('.dll') or file.endswith('.exe') or file.endswith('.pdb'):
            os.rename(builds + file, out + '\\' + file)

def build(architecture, type):
    command = 'msbuild -t:Build -p:Configuration=' + type + ';Platform=' + architecture + ';OutDir="..\..\.builds" -clp:ErrorsOnly -verbosity:quiet -nologo ./src'
    os.system(command)
    package(architecture)

if 'release' in sys.argv:
    MODE = 'release'
    print('Building x64 Release...')
    build('x64', 'Release')
    print('Building x86 Release...')
    build('x86', 'Release')
    print('Cleaning build files...')
    clean()
    print('Archiving bins...')
    archive()
    print('Done.')
else:
    MODE = 'debug'
    print('Building x64 Debug...')
    build('x64', 'Debug')
    print('Building x86 Debug...')
    build('x86', 'Debug')
    print('Cleaning build files...')
    clean()
    print('Done.')