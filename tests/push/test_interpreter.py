import unittest

from pyshgp.push.interpreter import PushInterpreter


class TestPushStateMethods(unittest.TestCase):

    def setUp(self):
        self.i = PushInterpreter()
        self.d = {'_auxiliary': [],
                  '_boolean': [],
                  '_char': [],
                  '_code': [],
                  '_exec': [],
                  '_float': [],
                  '_input': ['a', 'b', 'c'],
                  '_integer': [],
                  '_string': [],
                  '_vector_boolean': [],
                  '_vector_float': [],
                  '_vector_integer': [],
                  '_vector_string': []}
        self.i.state.from_dict(self.d)

    def test_len(self):
        self.assertEqual(len(self.i.state), 3)

    def test_from_dict(self):
        self.d['_integer'].append(5)
        self.i.state.from_dict(self.d)
        self.assertEqual(len(self.i.state), 4)
        self.assertEqual(self.i.state['_integer'].top_item(), 5)
        self.assertEqual(len(self.i.state['_integer']), 1)

    def test_pretty_print(self):
        self.i.state.pretty_print()


class TestPushInterpreterMethods(unittest.TestCase):

    def setUp(self):
        self.i = PushInterpreter()

    def test_reset(self):
        self.i.reset()

    def test_eval_atom_literal(self):
        self.i.eval_atom(5)
        self.assertEqual(self.i.state['_integer'][0], 5)

    def test_eval_atom_list(self):
        self.i.eval_atom([1, 2, 3, 4, 5])
        self.assertEqual(len(self.i.state['_exec']), 5)

    def test_eval_push(self):
        self.i.state['_exec'].push([1, 2, [3, 4], 5])
        self.i.eval_push()
        self.assertEqual(len(self.i.state['_integer']), 5)
        self.assertEqual(len(self.i.state['_exec']), 0)

    def test_run(self):
        outputs = self.i.run([7, 'hello'],
                             inputs=["a", "b", "c"],
                             output_types=['_string'])
        self.assertEqual(outputs, ['hello'])
