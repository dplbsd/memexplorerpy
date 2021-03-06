#!/usr/bin/env python2
import sys, time
import memproblem
import random as rand

# 1 - Generate p chromosomes of solution.
# 2 - Decode them and test fitness.
# 3 - If the stopping rule is given, return best solution.
# 4 - Sort by fitness.
# 5 - Classify by fitness.
# 6 - Copy elite solutions to next population.
# 7 - Generate mutant solutions.
# 8 - Crossover
# 9 - Goto 2
class brkga:
	n = 0
	p = 0
	pe = 0
	pm = 0
	rhoe = 0
	
	# Populations
	previous = []
	current = []

	# n: Number of genes in each chromosome.
	# p: Number of elements in each population.
	# pe: Percent of elite items into each population.
	# pm: Percent of mutants introduced at each generation into the population.
	# rhoe: Probability that an offspring inherits the allele of its elite parent.
	def __init__(self, pr, dec, n, p, s):
		def create_population():
			"""Create the whole population."""
			def create_chromosome():
				"""Create a chromosome."""
				return [rand.random() for i in range(self.n)]
			return [create_chromosome() for i in range(self.p)]

		self.n = n
		self.p = p
		self.pe = 0.2 
		self.pm = 0.1 
		self.rhoe = 0.7
		self.problem = pr
		rand.seed(s)
	
		# The decoder creates a solution using the chromosome.
		# It returns the rank of the solution.
		self.decoder = dec 
		self.current = self.rank(create_population())
		# Create copy
		self.previous = list(self.current)
		assert len(self.previous) == len(self.current) == self.p
		assert len(self.previous[0][1]) == len(self.current[0][1]) == self.n
		return None

	def rank(self, chromosomes):
		"""Decode and evaluate the cost of the current population."""
		return sorted([(self.decoder(ch, self.problem.copy()), ch) for ch in chromosomes])

	def evolve(self):
		"""Improves the current solutions."""
		def getElite():
			"""Get the best solutions."""
			eltotake = int(self.p * self.pe)
			elite = self.previous[:eltotake]
			nonelite = self.previous[eltotake:]
			return elite, nonelite

		def make_mutants():
			"""Creates set of mutants."""
			def mutate(index):
				"""Mutates the previous[index] chromosome."""
				return [rand.random() if rand.random() <= 0.5 else v for v in self.previous[index][1]]

			return [mutate(i) for i in range(self.p) if rand.random() < self.pm]

		def crossover(elite, nonelite, elems):
			"""Creates the new elements using an elite and a non-elite chromosome."""
			ret = []
			for i in range(elems):
				ei = rand.randint(0, len(elite)-1)
				ni = rand.randint(0, len(nonelite)-1)
					
				newelem = []
				for j in range(self.n):
					if rand.random() <= self.rhoe:
						newelem.append(elite[ei][1][j])
					else: newelem.append(nonelite[ni][1][j])
				ret.append( (self.decoder(newelem, self.problem), newelem) )
			return ret

		# getElite returns ranked chromsomes.
		elite, nonelite = getElite()
		mutants = self.rank(make_mutants())

		crossoverlen = self.p - len(elite) - len(mutants)
		crossover = crossover(elite, nonelite, crossoverlen)

		self.previous = list(self.current)
		self.current = sorted(elite + crossover + mutants)

		# Ensure decent length.
		if len(self.current) > self.p:
			self.current =  self.current[:self.p]
		if len(self.previous) > self.p:
			self.previous =  self.previous[:self.p]
		return

	def bestSolution(self):
		return self.current[0]

def decoder(ch, problem):
	"""Creates a solution greedily, and returns the fitness of the chromosome."""
	def is_allocable(dsi, mbi):
		"""Tries to allocate datastruct[i] into membank[j]."""
		if problem.membanks[mbi]['capacity'] - problem.cap_used[mbi] >= problem.datastructs[dsi]['size']:
			return True
		return False

	def allocate(dsi, mbi):
		"""Tries to allocate datastruct[i] into membank[j]."""
		if problem.membanks[mbi]['capacity'] - problem.cap_used[mbi] >= problem.datastructs[dsi]['size']:
			problem.X[dsi][mbi] = True
			problem.cap_used[mbi] += problem.datastructs[dsi]['size']
			return True
		return False

	matrixlen = len(problem.X)
	rowlen = len(problem.X[0])

	# Get the indexes from the chromosome.
	# The highest value chromosome will be the first datastruct allocated.
	queue = []
	indexes = []
	while len(queue) < len(ch):
		index = 0
		biggest = 0
		for i in range(len(ch)):
			if i not in queue and ch[i] > biggest:
				biggest = ch[i]
				index = i
		queue.append(index)
	
	# Put each datastruct greedily using the index.
	for i in queue:
		allocable = [j for j in range(problem.membanks_n+1) if is_allocable(i, j)]
		costs = [(problem.cost(i, j), j) for j in allocable]
		assert allocate(i, min(costs)[1]) == True

	return problem.calculate_cost()

# Testing function.
def do_brkga(filename, iters, p):
	problem = memproblem.read_problem(filename)
	brkgasolver = brkga(problem, dec=decoder, n=problem.datastructs_n, p=20, s=time.time())

	for i in range(iters):
		brkgasolver.evolve()
	del brkgasolver, problem
	return brkgasolver.bestSolution()


if __name__ == "__main__":
	print do_brkga(sys.argv[2], int(sys.argv[1]), 20)
