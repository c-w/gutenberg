# pylint: disable=C0111
# pylint: disable=R0903
# pylint: disable=R0904


from __future__ import absolute_import
import abc
import os
import shutil
import tempfile
import unittest

from gutenberg._util.abc import abstractclassmethod
from gutenberg._util.objects import all_subclasses
from gutenberg._util.os import makedirs
from gutenberg._util.os import remove


class TestAllSubclasses(unittest.TestCase):
    def test_all_subclasses(self):
        class Root(object):
            pass

        class AB(Root):
            pass

        class ABC(AB):
            pass

        class AD(Root):
            pass

        class ABAD(AB, AD):
            pass

        class ABADE(ABAD):
            pass

        self.assertItemsEqual(all_subclasses(Root), [AB, ABC, AD, ABAD, ABADE])
        self.assertSetEqual(all_subclasses(ABADE), set())


class TestAbstractClassMethod(unittest.TestCase):
    def test_abstractclassmethod(self):
        class ClassWithAbstractClassMethod(object):
            __metaclass__ = abc.ABCMeta

            @abstractclassmethod
            def method(cls):
                pass

        class ConcreteImplementation(ClassWithAbstractClassMethod):
            @classmethod
            def method(cls):
                pass

        with self.assertRaises(TypeError):
            ClassWithAbstractClassMethod()
        ConcreteImplementation()


class TestRemove(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.mkdtemp()
        self.temporary_file = tempfile.NamedTemporaryFile(delete=False).name

    def test_remove(self):
        for path in (self.temporary_file, self.temporary_directory):
            self.assertTrue(os.path.exists(path))
            remove(path)
            self.assertFalse(os.path.exists(path))


class TestMakedirs(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temporary_directory)

    def test_makedirs(self):
        path = os.path.join(self.temporary_directory, 'foo', 'bar', 'baz')
        self.assertFalse(os.path.exists(path))
        makedirs(path)
        self.assertTrue(os.path.exists(path))


if __name__ == '__main__':
    unittest.main()
