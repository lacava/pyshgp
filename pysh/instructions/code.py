# -*- coding: utf-8 -*-
"""
Created on Sun Jun  17, 2016

@author: Eddie
"""
from __future__ import absolute_import, division, print_function, unicode_literals


from .. import pysh_state
from .. import instruction as instr
from .. import utils as u

from . import registered_instructions as ri


exec_noop_instruction = instr.Pysh_Instruction('exec_noop',
														   lambda state: state,
														   stack_types = ['_exec'])
ri.register_instruction(exec_noop_instruction)

code_noop_instruction = instr.Pysh_Instruction('code_noop',
															lambda state: state,
															stack_types = ['_code'])
ri.register_instruction(code_noop_instruction)


def code_maker(pysh_type):
	def f(state):
		if len(state.stacks[pysh_type]) > 0:
			new_code = state.stacks[pysh_type].stack_ref(0)
			state.stacks[pysh_type].pop_item()
			state.stacks['_code'].push_item(new_code)
		return state
	instruction = instr.Pysh_Instruction('code_from' + pysh_type,
													f,
													stack_types = ['_code', pysh_type])
	if pysh_type == '_exec':
		instruction.parentheses = 1
	return instruction
ri.register_instruction(code_maker('_boolean'))
ri.register_instruction(code_maker('_float'))
ri.register_instruction(code_maker('_integer'))
ri.register_instruction(code_maker('_exec'))


def code_append(state):
	if len(state.stacks['_code']) > 1:
		new_item = u.ensure_list(state.stacks['_code'].stack_ref(0)) + u.ensure_list(state.stacks['_code'].stack_ref(1))
		state.stacks['_code'].pop_item()
		state.stacks['_code'].pop_item()
		state.stacks['_code'].push_item(new_item)
	return state
code_append_instruction = instr.Pysh_Instruction('code_append',
	                                                        code_append,
	                                                        stack_types = ['_code'])
ri.register_instruction(code_append_instruction)


def code_atom(state):
	if len(state.stacks['_code']) > 0:
		top_code = state.stacks['_code'].stack_ref(0)
		state.stacks['_code'].pop_item()
		state.stacks['_boolean'].push_item(not (type(top_code) == list))
	return state
code_atom_instruction = instr.Pysh_Instruction('code_atom',
														  code_atom,
														  stack_types = ['_code', '_boolean'])
ri.register_instruction(code_atom_instruction)


def code_car(state):
	if len(state.stacks['_code']) > 0 and len(u.ensure_list(state.stacks['_code'].stack_ref(0))) > 0:
		top_code = u.ensure_list(state.stacks['_code'].stack_ref(0))[0]
		state.stacks['_code'].pop_item()
		state.stacks['_code'].push_item(top_code)
	return state
code_car_instruction = instr.Pysh_Instruction('code_car',
														 code_car,
														 stack_types = ['_code'])
ri.register_instruction(code_car_instruction)


def code_cdr(state):
	if len(state.stacks['_code']) > 0:
		top_code = u.ensure_list(state.stacks['_code'].stack_ref(0))[1:]
		state.stacks['_code'].pop_item()
		state.stacks['_code'].push_item(top_code)
	return state		
code_cdr_instruction = instr.Pysh_Instruction('code_cdr',
														 code_cdr,
														 stack_types = ['_code'])
ri.register_instruction(code_cdr_instruction)


def code_cons(state):
	if len(state.stacks['_code']) > 1:
		new_item = [state.stacks['_code'].stack_ref(1)] + u.ensure_list(state.stacks['_code'].stack_ref(0))
		state.stacks['_code'].pop_item()
		state.stacks['_code'].push_item(new_item)
	return state
code_cons_instruction = instr.Pysh_Instruction('code_cons',
														  code_cons,
														  stack_types = ['_code'])
ri.register_instruction(code_cons_instruction)


def code_do(state):
	if len(state.stacks['_code']) > 0:
		top_code = state.stacks['_code'].stack_ref(0)
		state.stacks['_exec'].push_item(lambda: ri.get_instruction_by_name('_code_pop'))
		state.stacks['_exec'].push_item(top_code)
	return state
code_do_instruction = instr.Pysh_Instruction('code_do',
														code_do,
														stack_types = ['_code', '_exec'])
ri.register_instruction(code_do_instruction)



def code_do_star(state):
	if len(state.stacks['_code']) > 0:
		top_code = state.stacks['_code'].stack_ref(0)
		state.stacks['_exec'].push_item(top_code)
	return state
code_do_star_instruction = instr.Pysh_Instruction('code_do*',
															 code_do_star,
															 stack_types = ['_code', '_exec'])
ri.register_instruction(code_do_star_instruction)


def code_do_range(state):
	if len(state.stacks['_code']) > 0 and len(state.stacks['_integer']) > 1:
		to_do = state.stacks['_code'].stack_ref(0)
		current_index = state.stacks['_integer'].stack_ref(1)
		destination_index = state.stacks['_integer'].stack_ref(0)
		state.stacks['_integer'].pop_item()
		state.stacks['_integer'].pop_item()
		state.stacks['_code'].pop_item()

		increment = 0
		if current_index < destination_index:
			increment = 1
		elif current_index > destination_index:
			increment = -1

		if not increment == 0:
			state.stacks['_exec'].push_item([(current_index + increment), 
											  destination_index, 
											  lambda: ri.get_instruction_by_name('code_from_exec'), 
											  to_do,
											  lambda: ri.get_instruction_by_name('code_do*range')])
		state.stacks['_integer'].push_item(current_index)
		state.stacks['_exec'].push_item(to_do)
	return state
code_do_range_intruction = instr.Pysh_Instruction('code_do*range',
												  			 code_do_range,
												  			 stack_types = ['_exec', '_integer', '_code'])
ri.register_instruction(code_do_range_intruction)


def exec_do_range(state):
	'''
	Differs from code.do*range only in the source of the code and the recursive call.
	'''
	if len(state.stacks['_exec']) > 0 and len(state.stacks['_integer']) > 1:
		to_do = state.stacks['_exec'].stack_ref(0)
		current_index = state.stacks['_integer'].stack_ref(1)
		destination_index = state.stacks['_integer'].stack_ref(0)
		state.stacks['_integer'].pop_item()
		state.stacks['_integer'].pop_item()
		state.stacks['_exec'].pop_item()

		increment = 0
		if current_index < destination_index:
			increment = 1
		elif current_index > destination_index:
			increment = -1

		if not increment == 0:
			state.stacks['_exec'].push_item([(current_index + increment), 
											  destination_index, 
											  lambda: ri.get_instruction_by_name('_exec_do*range'), 
											  to_do])

		state.stacks['_integer'].push_item(current_index)
		state.stacks['_exec'].push_item(to_do)
	return state

exec_do_range_intruction = instr.Pysh_Instruction('exec_do*range',
												  			 exec_do_range,
												  			 stack_types = ['_exec', '_integer'],
												  			 parentheses = 1)
ri.register_instruction(exec_do_range_intruction)


def code_do_count(state):
	if not (len(state.stacks['_integer']) == 0 or state.stacks['_integer'].stack_ref(0) < 1 or len(state.stacks['_code']) == 0):
		to_push = [0, 
				   state.stacks['_integer'].stack_ref(0) - 1, 
				   lambda: ri.get_instruction_by_name('_code_from_exec'),
				   state.stacks['_code'].stack_ref(0),
				   lambda: ri.get_instruction_by_name('code_do*range')]
		state.stacks['_code'].pop_item()
		state.stacks['_integer'].pop_item()
		state.stacks['_exec'].push_item(to_push)
	return state

code_do_count_intruction = instr.Pysh_Instruction('code_do*count',
												  			 code_do_count,
												  			 stack_types = ['_exec', '_integer', '_code'])
ri.register_instruction(code_do_count_intruction)


def exec_do_count(state):
	'''
	differs from code.do*count only in the source of the code and the recursive call
	'''
	if not (len(state.stacks['_integer']) == 0 or state.stacks['_integer'].stack_ref(0) < 1 or len(state.stacks['_exec']) == 0):
		to_push = [0, 
				   state.stacks['_integer'].stack_ref(0) - 1, 
				   lambda: ri.get_instruction_by_name('_exec_do*range'),
				   state.stacks['_exec'].stack_ref(0)]
		state.stacks['_exec'].pop_item()
		state.stacks['_integer'].pop_item()
		state.stacks['_exec'].push_item(to_push)
	return state

exec_do_count_intruction = instr.Pysh_Instruction('exec_do*count',
												  			 exec_do_count,
												  			 stack_types = ['_exec', '_integer'],
												  			 parentheses = 1)
ri.register_instruction(exec_do_count_intruction)


def code_do_times(state):
	if not (len(state.stacks['_integer']) == 0 or state.stacks['_integer'].stack_ref(0) < 1 or len(state.stacks['_code']) == 0):
		to_push = [0,
		           state.stacks['_integer'].stack_ref(0) - 1,
		           lambda: ri.get_instruction_by_name('_code_from_exec'),
		           [lambda: ri.get_instruction_by_name('_integer_pop')] + u.ensure_list(state.stacks['_code'].stack_ref(0)),
		           lambda: ri.get_instruction_by_name('_code_do*range')]
		state.stacks['_code'].pop_item()
		state.stacks['_integer'].pop_item()
		state.stacks['_exec'].push_item(to_push)
code_do_times_intruction = instr.Pysh_Instruction('code_do*times',
												  			 code_do_times,
												  			 stack_types = ['_code', '_integer'])
ri.register_instruction(code_do_times_intruction)


def exec_do_times(state):
	'''
	differs from code.do*times only in the source of the code and the recursive call
	'''
	if not (len(state.stacks['_integer']) == 0 or state.stacks['_integer'].stack_ref(0) < 1 or len(state.stacks['_exec']) == 0):
		to_push = [0, 
				   state.stacks['_integer'].stack_ref(0) - 1, 
				   lambda: ri.get_instruction_by_name('exec_do*range'),
				   [lambda: ri.get_instruction_by_name('_integer_pop')] + u.ensure_list(state.stacks['_exec'].stack_ref(0))]
		state.stacks['_exec'].pop_item()
		state.stacks['_integer'].pop_item()
		state.stacks['_exec'].push_item(to_push)
	return state

exec_do_times_intruction = instr.Pysh_Instruction('exec_do*times',
												  			 exec_do_times,
												  			 stack_types = ['_exec', '_integer'],
												  			 parentheses = 1)
ri.register_instruction(exec_do_times_intruction)


def exec_while(state):
	if len(state.stacks['_exec']) > 0:
		if len(state.stacks['_boolean']) == 0:
			state.stacks['_exec'].pop_item()
		elif not state.stacks['_boolean'].stack_ref(0):
			state.stacks['_exec'].pop_item()
			state.stacks['_boolean'].pop_item()
		else:
			block = state.stacks['_exec'].stack_ref(0)
			state.stacks['_exec'].push_item(lambda: ri.get_instruction_by_name('_exec_while'))
			state.stacks['_exec'].push_item(block)
			state.stacks['_boolean'].pop_item()
	return state
exec_while_intruction = instr.Pysh_Instruction('exec_while',
												  	      exec_while,
												  		  stack_types = ['_exec', '_boolean'],
												  		  parentheses = 1)
ri.register_instruction(exec_while_intruction)


def exec_do_while(state):
	if len(state.stacks['_exec']) > 0:
			block = state.stacks['_exec'].stack_ref(0)
			state.stacks['_exec'].push_item(exec_while_intruction)
			state.stacks['_exec'].push_item(block)
	return state
exec_do_while_intruction = instr.Pysh_Instruction('exec_do*while',
															 exec_do_while,
															 stack_types = ['_exec', '_boolean'],
															 parentheses = 1)
ri.register_instruction(exec_do_while_intruction)



# Code Map
