import random
import sys
import re

# Class containing the whole problem set.
# We can set up the maximum number of elements, and its maximum value.
class MemProblem():
	cap_used = []
	
	# Class needs the number of datastructs, membanks, and conflicts.
	def __init__(self, datastructs, membanks, conflicts, penalty):
		self.datastructs_n = len(datastructs)  
		self.membanks_n = len(membanks)
		self.conflicts_n = len(conflicts)

		self.conflicts = conflicts
		self.membanks = membanks
		self.datastructs = datastructs
		self.penalty = penalty
		self.membanks.append({'capacity': sys.maxint})

		self.X = []
		for i in range(0, len(self.datastructs)):
			self.X.append([False] * len(self.membanks))
		# Include external memory.
		for i in range(0, self.membanks_n + 1):
			self.cap_used.append(0)

	# Print solution
	def print_problem(self):
		print self.datastructs
		print self.membanks
		print self.conflicts
		print self.penalty

	def print_solution(self):
		for row in self.X:
			print row

	def results(self):
		return "{cost}, {usage}".format(cost=self.calculate_cost(), usage=self.print_usage())

	def print_usage(self):
		remaining_capacities_acc = 0;
		capacity_acc = 0;
		for j in range(0, len(self.membanks)-1):
			remaining_capacity = 0
			for ai in range(0, len(self.X)):
				if self.X[ai][j] == True:
					remaining_capacity += self.datastructs[ai]['size']
				remaining_capacities_acc += remaining_capacity
				capacity_acc += self.membanks[j]['capacity']
		return float(remaining_capacities_acc)/float(capacity_acc)

	def calculate_cost(self):
		cost = 0
		
		# Data structs cost
		for i in range(0, len(self.datastructs)):
			for j in range(0, len(self.membanks)-1):
				if self.X[i][j] == True:
					cost += self.datastructs[i]['cost']
		
		# Conflicts cost
		for conf in self.conflicts:
			cost = cost + conf['cost'] * conf['status']
		
		# External storage cost
		for i in range(0, len(self.X)):
			if self.X[i][-1] == True:
				cost += self.penalty * self.datastructs[i]['cost']
		return cost
	
	# Check correctness of solution.
	# Returns false if incorrect.
	def is_correct(self):
		#Check feasability of the solution.
		for i in self.X:
			trues = 0
			for j in i:
				if j == True:
					trues += 1
			if trues != 1:
				return False

		# We'll need to set the correct cap_used.
		for i in range(len(self.cap_used)):
			self.cap_used[i] = 0

		# Ensure that each datastructure fits into its membank.
		# Ensure that each membank is not overflowed.
		for i in range(len(self.X)):
			for j in range(len(self.X[i])):
				if self.X[i][j] == True:
					ds = self.datastructs[i]['size']
					mem = self.membanks[j]['capacity']

					self.cap_used[j] += ds
					if self.cap_used[j] > mem:
						return False
		return True

	def cost(self, i, j):
		cost = self.datastructs[i]['cost'] #Access cost of i
		if j == len(self.membanks)-1:
			cost = cost*self.penalty

		for conflict in self.conflicts:
			if conflict['a'] == i or conflict['b'] == i:
				if self.X[i][j] == True:
					cost += conflict['cost'] * self.conflict_status(conflict) * conflict['cost']
				else:
					self.X[i][j] = True
					cost += conflict['cost'] * self.conflict_status(conflict) * conflict['cost']
					self.X[i][j] = False

		return cost

	def whereis(self, i):
		for j in range(0, len(self.X[i])):
			if self.X[i][j] == True:
				return j
		return None

	def update_conflicts(self):
		for conflict in self.conflicts:
			conflict['status'] = self.conflict_status(conflict)

	def conflict_status(self, conflict):
		cost = 0
		a = conflict['a']
		b = conflict['b']
		j1 = self.whereis(a)
		j2 = self.whereis(b)

		
		if j1 == None or j2 == None:
			return 0

		elif j1 == j2:

			if j1 == len(self.membanks)-1 and j2 == len(self.membanks)-1:
				return self.penalty*2
			else:
				return 1

		elif j1 == len(self.membanks)-1 or j2 == len(self.membanks)-1:
			return self.penalty

		return 0

	def write_file(self, filename):
		f = open(filename, 'w')
		f.write('num_data_structures = {datastructs};\n'.format(datastructs=self.datastructs_n))
		f.write('num_memory_banks = {membanks};\n'.format(membanks=self.membanks_n))
		f.write('p = {penalty};\n'.format(penalty=self.penalty))
		f.write('conflicts = {conflicts};\n\n'.format(conflicts=self.conflicts_n))
		
		#Datastruct sizes
		f.write('s = [')
		for datastruct in self.datastructs[:-1]:
			f.write('{size}, '.format(size=datastruct['size']))
		f.write('{size}];\n'.format(size=self.datastructs[-1]['size']))
		
		#Membank sizes
		f.write('c = [')
		for membank in self.membanks[:-2]:
			f.write('{capacity}, '.format(capacity=membank['capacity']))
		f.write('{capacity}];\n'.format(capacity=self.membanks[-2]['capacity']))

		#Datastruct costs
		f.write('e = [')
		for datastruct in self.datastructs[:-1]:
			f.write('{cost}, '.format(cost=datastruct['cost']))
		f.write('{cost}];\n'.format(cost=self.datastructs[-1]['cost']))

		#Conflict costs
		f.write('d = [')
		for conflict in self.conflicts[:-1]:
			f.write('{cost}, '.format(cost=conflict['cost']))
		f.write('{cost}];\n\n'.format(cost=self.conflicts[-1]['cost']))

		#A
		f.write('A = [')
		for conflict in self.conflicts[:-1]:
			f.write('{a}, '.format(a=conflict['a']))
		f.write('{a}];\n'.format(a=self.conflicts[-1]['a']))

		#B
		f.write('B = [')
		for conflict in self.conflicts[:-1]:
			f.write('{b}, '.format(b=conflict['b']))
		f.write('{b}];\n'.format(b=self.conflicts[-1]['b']))

	def copy(self):
		datastructs = []
		membanks = []
		conflicts = []
		
		for datastruct in self.datastructs:
			datastructs.append({'size': datastruct['size'] ,'cost': datastruct['cost']})

		for membank in self.membanks:
			membanks.append({'capacity': membank['capacity']})

		for conflict in self.conflicts:
			conflicts.append({'a': conflict['a'] ,'b': conflict['b'], 'cost': conflict['cost'], 'status': conflict['status']})

		membanks.pop()

		problem = MemProblem(datastructs=datastructs, membanks=membanks, conflicts=conflicts, penalty=self.penalty)
		
		for row in range(0, len(self.X)):
			problem.X[row] = list(self.X[row])
		problem.update_conflicts()
		
		return problem

	# Create a random problem.
def read_problem(filename):
	data = open(filename, 'r').read()
	s = [int(numeric_string) for numeric_string in re.search('s = \[((?:\d+,\s*)*\d+)\];', data).group(1).replace(' ', '').split(',')]
	d = [int(numeric_string) for numeric_string in re.search('d = \[((?:\d+,\s*)*\d+)\];', data).group(1).replace(' ', '').split(',')]
	c = [int(numeric_string) for numeric_string in re.search('c = \[((?:\d+,\s*)*\d+)\];', data).group(1).replace(' ', '').split(',')]
	e = [int(numeric_string) for numeric_string in re.search('e = \[((?:\d+,\s*)*\d+)\];', data).group(1).replace(' ', '').split(',')]
	A = [int(numeric_string) for numeric_string in re.search('A = \[((?:\d+,\s*)*\d+)\];', data).group(1).replace(' ', '').split(',')]
	B = [int(numeric_string) for numeric_string in re.search('B = \[((?:\d+,\s*)*\d+)\];', data).group(1).replace(' ', '').split(',')]
	penalty = int(re.search('p = (\d+);', data).group(1))

	conflicts = []
	datastructs = []
	membanks = []

	for (a, b, cost) in zip(A, B, d):
		conflicts.append({'a': a, 'b':b, 'cost': cost, 'status': 0})
	
	for (size, cost) in zip(s, e):
		datastructs.append({'size': size, 'cost': cost})

	for capacity in c:
		membanks.append({'capacity': capacity})

	return MemProblem(datastructs=datastructs, membanks=membanks, conflicts=conflicts, penalty=penalty)



def random_problem(seed, dss_min, dss_max, dsc_min, dsc_max, ds_n, mem_min, mem_max, mem_n, c_min, c_max, c_n, p_min, p_max):
	#Penalty
	penalty = random.randint(p_min, p_max)
		
	# Create random membanks.
	membanks = [0] * mem_n
	for i in range(0, mem_n):
		membanks[i] = { 'capacity': random.randint(mem_min, mem_max) }

	# Create random datastructs.
	datastructs = [0] * ds_n
	for i in range(0, ds_n):
		datastructs[i] = { 'size': random.randint(dss_min, dss_max), 'cost': random.randint(dsc_min, dsc_max) }
	# Create random conflicts
	conflicts = [0] * c_n
	for i in range(0, c_n):
		conflicts[i] = {
			'a': random.randint(0, ds_n-1), 
			'b': random.randint(0, ds_n-1),
			'cost': random.randint(c_min, c_max),
			'status': 0
		}		

	return MemProblem(datastructs=datastructs, membanks=membanks, conflicts=conflicts, penalty=penalty)
