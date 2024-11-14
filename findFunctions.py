"""
  Module: Find all functions and global constants defined in a module file.
  Author: ZANG Zhengrong
  Date: 2024/11/06
"""

import ast
from collections import defaultdict
from datetime import timedelta
from glob import glob
from sys import argv
from timeit import timeit

###############################################################################
def addParentReferences(tree):
    """ Add parent references to AST node to enable module-level detection. """
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child.parent = node

###############################################################################
def findDefinitions(filePath):
    with open(filePath, 'r', encoding='UTF-8') as file:
        tree = ast.parse(file.read())

    addParentReferences(tree)
    functions = []
    constants = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions.append(node.name)
        elif isinstance(node, ast.Assign) and isinstance(node.parent, ast.Module):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    constants.append(target.id)
    return functions, constants

###############################################################################
def findRefrences(filePath):
    """ Find all module.function or module.constant references in a Python file. """
    with open(filePath, 'r', encoding='UTF-8') as file:
        tree = ast.parse(file.read())

    references = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                fullReference = f'{node.func.value.id}.{node.func.attr}'
                references.append(fullReference)
        elif isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            fullReference = f'{node.value.id}.{node.attr}'
            references.append(fullReference)
    return references

###############################################################################
def analyzeProjectFiles(mainDir, modulesDir):
    # Step1: Collect all finctions and constants definitions from myModules subfolder
    definedInModules = {}#OrderedDict()
    for filePath in glob(f'{modulesDir}/*.py'):
        moduleName = filePath.split('\\')[-1].replace('.py', '')
        functions, constants = findDefinitions(filePath)
        for func in functions:
            definedInModules[f'{moduleName}.{func}'] = filePath
        for const in constants:
            definedInModules[f'{moduleName}.{const}'] = filePath

    # Step2: Track where each function and constant is referenced in both folders
    referenceUsage = defaultdict(set)
    for searchDir in [mainDir, modulesDir]:
        for filePath in glob(f'{searchDir}/*.py'):
            references = findRefrences(filePath)
            for ref in references:
                if ref in definedInModules:
                    referenceUsage[ref].add(filePath)

    # Find functions and constants used only in one file
    uniqueReferenceUsage = {ref: files for ref, files in referenceUsage.items() #}
                            if len(files) == 1}
    return definedInModules, uniqueReferenceUsage

###############################################################################
def showSortByReference(definedInModules, uniqueReferenceUsage):
    # 2. Sort by reference (function or constant name)
    sortedUniqueReferenceUsage = sorted(uniqueReferenceUsage.items())
    lastModule = ''
    lastFile = ''
    for ref, files in sortedUniqueReferenceUsage:
        moduleFile = definedInModules[ref]
        if lastModule != moduleFile:
            print(f'\nin {moduleFile}:')
            lastModule = moduleFile
        for main in files:
            if lastFile != main:
                print(f'\n  Only Used in {main}')
                lastFile = main
        print(f'    {ref.split('.')[-1]}')

###############################################################################
def showSortByModuleFile(definedInModules, uniqueReferenceUsage):
    # 1. Sort by module file (if you want to check which module files are involved)
    sortedUniqueReferenceUsage = sorted(uniqueReferenceUsage.items(), key=lambda x: definedInModules[x[0]])
    lastModule = ''
    lastFile = ''
    for ref, files in sortedUniqueReferenceUsage:
        moduleFile = definedInModules[ref]
        if lastModule != moduleFile:
            print(f'\nin {moduleFile}:')
            lastModule = moduleFile
        for main in files:
            if lastFile != main:
                print(f'\n  Only Used in {main}')
                lastFile = main
        print(f'    {ref.split('.')[-1]}')

###############################################################################
def showSortByReferenceUsage(definedInModules, uniqueReferenceUsage):
    # 3. Sort by reference usage in main file (alphabetical order of file names)
    sortedUniqueReferenceUsage = sorted(uniqueReferenceUsage.items(), key=lambda x: sorted(x[1])[0])
    lastModule = ''
    lastFile = ''
    for ref, files in sortedUniqueReferenceUsage:
        for main in files:
            if lastFile != main:
                print(f'\nOnly Used in {main}')
                lastFile = main
            moduleFile = definedInModules[ref]
            if lastModule != moduleFile:
                print(f'\n  in {moduleFile}:')
                lastModule = moduleFile
            print(f'    {ref.split('.')[-1]}')

###############################################################################
def main():
    mainDir = 'C:\\zang\\python\\RocketLaunch'
    modulesDir = 'myModules'
    definedInModules, uniqueReferenceUsage = analyzeProjectFiles(mainDir, modulesDir)
    
    if len(argv) > 1:
        if argv[1] == '1':
            showSortByModuleFile(definedInModules, uniqueReferenceUsage)
        elif argv[1] == '2':
            showSortByReference(definedInModules, uniqueReferenceUsage)
        else:
            showSortByReferenceUsage(definedInModules, uniqueReferenceUsage)
    else:
        showSortByReference(definedInModules, uniqueReferenceUsage)

###############################################################################
def showRunTime(func):
    result = timeit(func, number=1, globals=globals())
    print(f'\nFinished in {timedelta(seconds=result)}')

if __name__ == '__main__':
    showRunTime('main()')
