import numpy as np
from collections import namedtuple

ProductionSolution = namedtuple('ProductionSolution', ['supply', 'wages', 'allocation', 'jacobi'])

# adds an additonal entry at the end of prices which corresponds to one additional listenting for the price of gold. It's price is always 1 since prices are listed in gold.
def extended_prices(prices):
    return np.append(prices, 1)

class Producer:
    def __init__(self, production_matrix):
        self.production_matrix = production_matrix

    def num_tasks(self):
        return self.production_matrix.shape[0]

    def allocation_vector(self):
        nt = self.num_tasks()
        return np.full(nt, 1/nt)

    def extended_supply(self, allocation):
        return self.production_matrix.T @ np.sqrt(allocation)

    def wages(self, allocation, eprices):
        return eprices @ self.extended_supply(allocation)

    def produce(self, prices):
        assert(prices.size + 1 == self.production_matrix.shape[1])
        eprices = extended_prices(prices)

        # we first remove all tasks which result in negative income if all the necessary goods are bought at current prices
    
        # compute for each task how much money it makes
        payoff_one_unit = self.production_matrix @ eprices
    
        # remove money loosing tasks from the production matrix
        tasks_to_cancel = payoff_one_unit < 0
        pm = self.production_matrix.copy()
        pm[tasks_to_cancel,] = 0
    
        ep = pm @ eprices
        epsq = ep * ep
        lambda_squared = np.sum(epsq)
        allocation = epsq / lambda_squared
    
        lbd = np.sqrt(lambda_squared)
        prod_squared = pm * pm
        jacobi_diagonal = 1 / lbd * np.sum(prod_squared, axis=0)
        assert (allocation >= 0).all()
        assert (allocation <= 1).all()
        return ProductionSolution(self.extended_supply(allocation)[:-1],
                                  self.wages(allocation, eprices),
                                  allocation,
                                  jacobi_diagonal[:-1])
