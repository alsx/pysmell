import unittest

from vimhelper import findWord, findBase
from idehelper import findCompletions


def compMeth(name, klass):
    return dict(word=name, abbr='%s()' % name, kind='m', menu='Module:%s' % klass, dup='1')
def compFunc(name, args=''):
    return dict(word=name, abbr='%s(%s)' % (name, args), kind='f', menu='Module', dup='1')
def compConst(name):
    return dict(word=name, kind='d', menu='Module', dup='1')
def compProp(name, klass):
    return dict(word=name, kind='m', menu='Module:%s' % klass, dup='1')
def compClass(name):
    return dict(word=name, abbr='%s()' % name,  kind='t', menu='Module', dup='1')

class MockVim(object):
    class _current(object):
        class _window(object):
            cursor = (-1, -1)
        buffer = []
        window = _window()
    current = _current()
    command = lambda _, __:Non
    def eval(*_):
        pass

class CompletionTest(unittest.TestCase):
    def setUp(self):
        self.pysmelldict = {
                'CONSTANTS' : ['Module.aconstant', 'Module.bconst'],
                'FUNCTIONS' : [('Module.a', [], ''), ('Module.arg', [], ''), ('Module.b', ['arg1', 'arg2'], '')],
                'CLASSES' : {
                    'Module.aClass': {
                        'constructor': [],
                        'bases': ['object', 'ForeignModule.alien'],
                        'properties': ['aprop', 'bprop'],
                        'methods': [('am', [], ''), ('bm', [], ())]
                    },
                    'Module.bClass': {
                        'constructor': [],
                        'bases': ['Module.aClass'],
                        'properties': ['cprop', 'dprop'],
                        'methods': [('cm', [], ''), ('dm', [], ())]
                    }
                    
                }
            }
        self.nestedDict = {
                'CONSTANTS' : [],
                'FUNCTIONS' : [],
                'CLASSES' : {
                    'Nested.Package.Module.Class': {
                        'constructor': [],
                        'bases': [],
                        'properties': ['cprop'],
                        'methods': []
                    }
                    
                }
        }
        import vimhelper
        vimhelper.vim = self.vim = MockVim()

    def testFindBaseName(self):
        self.vim.current.buffer = ['aaaa', 'bbbb', 'cccc']
        self.vim.current.window.cursor =(2, 2)
        index = findBase(self.vim)
        word = findWord(self.vim, 2, 'bbbb')
        self.assertEquals(index, 0)
        self.assertEquals(word, 'bb')

    def testFindBaseMethodCall(self):
        self.vim.current.buffer = ['aaaa', 'a.bbbb(', 'cccc']
        self.vim.current.window.cursor =(2, 7)
        index = findBase(self.vim)
        word = findWord(self.vim, 7, 'a.bbbb(')
        self.assertEquals(index, 2)
        self.assertEquals(word, 'a.bbbb(')

    def testFindBaseFuncCall(self):
        self.vim.current.buffer = ['aaaa', 'bbbb(', 'cccc']
        self.vim.current.window.cursor =(2, 5)
        index = findBase(self.vim)
        word = findWord(self.vim, 5, 'bbbb(')
        self.assertEquals(index, 0)
        self.assertEquals(word, 'bbbb(')

    def testFindBaseNameIndent(self):
        self.vim.current.buffer = ['aaaa', '    bbbb', 'cccc']
        self.vim.current.window.cursor =(2, 6)
        index = findBase(self.vim)
        word = findWord(self.vim, 6, '    bbbb')
        self.assertEquals(index, 4)
        self.assertEquals(word, 'bb')

    def testFindBaseProp(self):
        self.vim.current.buffer = ['aaaa', 'hehe.bbbb', 'cccc']
        self.vim.current.window.cursor =(2, 7)
        index = findBase(self.vim)
        word = findWord(self.vim, 7, 'hehe.bbbb')
        self.assertEquals(index, 5)
        self.assertEquals(word, 'hehe.bb')

    def testFindBasePropIndent(self):
        self.vim.current.buffer = ['aaaa', '    hehe.bbbb', 'cccc']
        self.vim.current.window.cursor =(2, 11)
        index = findBase(self.vim)
        word = findWord(self.vim, 11, '    hehe.bbbb')
        self.assertEquals(index, 9)
        self.assertEquals(word, 'hehe.bb')

    def testCompletions(self):
        compls = findCompletions(None, '', '', 'b', 1, 1, 'b', self.pysmelldict)
        expected = [compFunc('b', 'arg1, arg2'), compClass('bClass'), compConst('bconst')]
        self.assertEquals(compls, expected)

    def testCompleteMembers(self):
        compls = findCompletions(None, '', '', 'somethign.a', 1, 11, 'a', self.pysmelldict)
        expected = [compMeth('am', 'aClass'), compProp('aprop', 'aClass')]
        self.assertEquals(compls, expected)

    def testCompleteArgumentListsPropRightParen(self):
        compls = findCompletions(None, '', '', 'salf.bm()', 1, 8, 'bm(', self.pysmelldict)
        orig = compMeth('bm', 'aClass')
        orig['word'] = orig['abbr'][:-1]
        self.assertEquals(compls, [orig])
        
    def testCompleteArgumentListsProp(self):
        compls = findCompletions(None, '', '', 'salf.bm(', 1, 8, 'bm(', self.pysmelldict)
        orig = compMeth('bm', 'aClass')
        orig['word'] = orig['abbr']
        self.assertEquals(compls, [orig])
        
    def testCompleteArgumentListsRightParen(self):
        compls = findCompletions(None, '', '', '   b()', 1, 5, 'b(', self.pysmelldict)
        orig = compFunc('b', 'arg1, arg2')
        orig['word'] = orig['abbr'][:-1]
        self.assertEquals(compls, [orig])

    def testCompleteArgumentLists(self):
        compls = findCompletions(None, '', '', '  b(', 1, 4, 'b(', self.pysmelldict)
        orig = compFunc('b', 'arg1, arg2')
        orig['word'] = orig['abbr']
        self.assertEquals(compls, [orig])

    def testInferSelfSimple(self):
        source = dedent("""\
            import something
            class AClass(object):
                def amethod(self, other):
                    other.do_something()
                    self.

                def another(self):
                    pass
        """)
        klass = infer(source, 5)
        self.assertEquals(klass, 'AClass')

    def testInferSelfMultipleClasses(self):
        
        source = dedent("""\
            import something
            class AClass(object):
                def amethod(self, other):
                    other.do_something()
                    class Sneak(object):
                        def sth(self):
                            class EvenSneakier(object):
                                pass
                            pass
                    pass

                def another(self):
                    pass



            class BClass(object):
                def newmethod(self, something):
                    wibble = [i for i in self.a]
                    pass

                def newerMethod(self, somethingelse):
                    if Bugger:
                        self.ass
        """)
        
        self.assertEquals(infer(source, 1), None, 'no class yet!')
        for line in range(2, 5):
            klass = infer(source, line)
            self.assertEquals(klass, 'AClass', 'wrong class %s in line %d' % (klass, line))

        for line in range(5, 7):
            klass = infer(source, line)
            self.assertEquals(klass, 'Sneak', 'wrong class %s in line %d' % (klass, line))

        for line in range(7, 9):
            klass = infer(source, line)
            self.assertEquals(klass, 'EvenSneakier', 'wrong class %s in line %d' % (klass, line))

        line = 9
        klass = infer(source, line)
        self.assertEquals(klass, 'Sneak', 'wrong class %s in line %d' % (klass, line))

        for line in range(10, 17):
            klass = infer(source, line)
            self.assertEquals(klass, 'AClass', 'wrong class %s in line %d' % (klass, line))

        for line in range(17, 51):
            klass = infer(source, line)
            self.assertEquals(klass, 'BClass', 'wrong class %s in line %d' % (klass, line))


    def testCompleteWithSelfInfer(self):
        source = dedent("""\
            class aClass(object):
                def sth(self):
                    self.
        
        """)
        compls = findCompletions(None, 'Module.py', source, "%sself." % (' ' * 8), 3, 13, '', self.pysmelldict)
        expected = [compMeth('am', 'aClass'), compProp('aprop', 'aClass'), compMeth('bm', 'aClass'), compProp('bprop', 'aClass')]
        self.assertEquals(compls, expected)

    def testCompletionsWithFullPath(self):
        source = dedent("""\
            class aClass(object):
                def sth(self):
                    self.
        
        """)
        compls = findCompletions(None,
                            r'C:\DevFolder\BlahBlah\APackageYouDontKnowAbout\Module.py', source,
                            "%sself." % (' ' * 8), 3, 13, '', self.pysmelldict)
        expected = [compMeth('am', 'aClass'), compProp('aprop', 'aClass'), compMeth('bm', 'aClass'), compProp('bprop', 'aClass')]
        self.assertEquals(compls, expected)

    def testCompletionsWithPackages(self):
        source = dedent("""\
            class Class(object):
                def sth(self):
                    self.
        
        """)
        expected = [dict(word='cprop', kind='m', menu='Nested.Package.Module:Class', dup='1')]
        compls = findCompletions(None,
                            r'C:\DevFolder\BlahBlah\Nested\Package\Module.py', source,
                            "%sself." % (' ' * 8), 3, 13, '', self.nestedDict)
        self.assertEquals(compls, expected)

    def testKnowAboutClassHierarchies(self):
        source = dedent("""\
            class bClass(aClass):
                def sth(self):
                    self.
        
        """)
        compls = findCompletions(None, 'Module.py', source, "%sself." % (' ' * 8), 3, 13, '', self.pysmelldict)
        expected = [compMeth('am', 'aClass'), compProp('aprop', 'aClass'),
                    compMeth('bm', 'aClass'), compProp('bprop', 'aClass'),
                    compMeth('cm', 'bClass'), compProp('cprop', 'bClass'),
                    compMeth('dm', 'bClass'), compProp('dprop', 'bClass')]
        self.assertEquals(compls, expected)
        source = dedent("""\
            class cClass(object):
                def sth(self):
                    self.
        
        """)
        self.assertEquals(findCompletions(None, 'Module.py', source, "%sself." % (' ' * 8), 3, 13, '', self.pysmelldict), [])


    def testCamelGroups(self):
        from idehelper import camelGroups
        def assertCamelGroups(word, groups):
            self.assertEquals(list(camelGroups(word)), groups.split())
        assertCamelGroups('alaMaKota', 'ala Ma Kota')
        assertCamelGroups('AlaMaKota', 'Ala Ma Kota')
        assertCamelGroups('isHTML', 'is H T M L')
        assertCamelGroups('ala_ma_kota', 'ala _ma _kota')

    def testMatchers(self):
        from idehelper import (matchCaseSensitively, matchCaseInsetively,
                matchCamelCased, matchSmartass, matchFuzzyCS, matchFuzzyCI)
        def assertMatches(base, word):
            msg = "should complete %r for %r with %s" % (base, word, testedFunction.__name__)
            uncurried = testedFunction(base)
            self.assertTrue(uncurried(word), msg +  "for the first time")
            self.assertTrue(uncurried(word), msg + "for the second time")
        def assertDoesntMatch(base, word):
            msg = "shouldn't complete %r for %r with %s" % (base, word, testedFunction.__name__)
            uncurried = testedFunction(base)
            self.assertFalse(uncurried(word), msg +  "for the first time")
            self.assertFalse(uncurried(word), msg + "for the second time")
        def assertStandardMatches():
            assertMatches('Ala', 'Ala')
            assertMatches('Ala', 'AlaMaKota')
            assertMatches('ala_ma_kota', 'ala_ma_kota')
            assertMatches('', 'AlaMaKota')
            assertDoesntMatch('piernik', 'wiatrak')
        def assertCamelMatches():
            assertMatches('AMK', 'AlaMaKota')
            assertMatches('aM', 'alaMaKota')
            assertMatches('aMK', 'alaMaKota')
            assertMatches('aMaKo', 'alaMaKota')
            assertMatches('alMaK', 'alaMaKota')
            assertMatches('a_ma_ko', 'ala_ma_kota')
            assertDoesntMatch('aleMbiK', 'alaMaKota')
            assertDoesntMatch('alaMaKotaIPsaIRybki', 'alaMaKota')

        testedFunction = matchCaseSensitively
        assertStandardMatches()
        assertDoesntMatch('ala', 'Alamakota')
        assertDoesntMatch('ala', 'Ala')

        testedFunction = matchCaseInsetively
        assertStandardMatches()
        assertMatches('ala', 'Alamakota')
        assertMatches('ala', 'Ala')
        
        testedFunction = matchCamelCased
        assertStandardMatches()
        assertCamelMatches()
        assertMatches('aMK', 'alaMaKota')
        assertDoesntMatch('almako', 'ala_ma_kota')
        assertDoesntMatch('almako', 'alaMaKota')
        assertDoesntMatch('alkoma', 'alaMaKota')

        testedFunction = matchSmartass
        assertStandardMatches()
        assertCamelMatches()
        assertMatches('amk', 'alaMaKota')
        assertMatches('AMK', 'alaMaKota')
        assertMatches('almako', 'ala_ma_kota')
        assertMatches('almako', 'alaMaKota')
        assertDoesntMatch('alkoma', 'alaMaKota')

        testedFunction = matchFuzzyCS
        assertStandardMatches()
        assertCamelMatches()
        assertMatches('aMK', 'alaMaKota')
        assertMatches('aaMKa', 'alaMaKota')
        assertDoesntMatch('almako', 'alaMaKota')
        assertDoesntMatch('amk', 'alaMaKota')
        assertDoesntMatch('alkoma', 'alaMaKota')

        testedFunction = matchFuzzyCI
        assertStandardMatches()
        assertCamelMatches()
        assertMatches('aMK', 'alaMaKota')
        assertMatches('aaMKa', 'alaMaKota')
        assertMatches('almako', 'alaMaKota')
        assertMatches('amk', 'alaMaKota')
        assertDoesntMatch('alkoma', 'alaMaKota')


if __name__ == '__main__':
    unittest.main()