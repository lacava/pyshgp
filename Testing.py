import pysh_random
import pysh_interpreter

import pysh_plush_translation as translate
import pysh_globals as g

gn = pysh_random.random_plush_genome(50)
print gn
print

prog = translate.translate_plush_genome_to_push_program(gn)
print prog
print

interpreter = pysh_interpreter.Pysh_Interpreter()
interpreter.run_push(prog)
interpreter.state.pretty_print()

print g.pysh_argmap['atom_generators']

######################################
# Broken programs

