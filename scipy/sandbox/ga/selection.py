#genetic algorithm selection routines
#based on galib.
#exception - these classes only work on the scaled fitness

import numpy as np

from ga_util import GAError
from prng import prng

class selector(object):
    def update(self,pop):
        pass
    def select(self,pop):
        raise GAError('selector.select() must be overridden')
    def clear(self):
        pass

class uniform_selector(selector):
    def select(self,pop,cnt = 1):
        if cnt == 1:
            return prng.choice(pop)
        res = []
        for i in range(cnt):
            res.append(prng.choice(pop))
        return res

#class rank_selector(selector):
#    def select(self,pop,cnt = 1):
#        pop.sort()
#        studliest = pop[0].fitness()
#        # XXX: y?
#        tied_for_first = [x for x in pop if x.fitness() == y]
#        if cnt == 1:
#            return prng.choice(tied_for_first)
#        res = []
#        for i in range(cnt):
#            res.append(prng.choice(tied_for_first))
#        return res

#scores must all be positive
class roulette_selector(selector):
    def update(self,pop):
        self.pop = pop[:]
        sz = len(pop)
        if not sz:
            raise GAError('srs_selector - the pop size is 0!')
        f =self.pop.fitnesses()
        f_max = max(f); f_min = min(f)
        if not ( (f_max >= 0 and f_min >= 0) or
                   (f_max <= 0 and f_min <= 0)):
            raise GAError('srs_selector requires all fitnesses values to be either strictly positive or strictly negative')
        if f_max == f_min:
            f = np.ones_like(f)
        self.dart_board = np.add.accumulate(f / sum(f,axis=0))

    def select(self,pop,cnt = 1):
        returns = []
        for i in range(cnt):
            dart = prng.random()
            idx = 0
            #binary search would be faster
            while dart > self.dart_board[idx]:
                idx = idx + 1
            returns.append(self.pop[idx])
        if cnt == 1:
            return returns[0]
        else:
            return returns

    def clear(self):
        del self.pop

#scores must all be positive
class srs_selector(selector):
    def update(self,pop):
        sz = len(pop)
        if not sz:
            raise GAError('srs_selector - the pop size is 0!')
        f =pop.fitnesses()
        f_max = max(f); f_min = min(f)
        if not ( (f_max >= 0. and f_min >= 0.) or
                   (f_max <= 0. and f_min <= 0.)):
            raise GAError('srs_selector requires all fitnesses values to be either strictly positive or strictly negative - min %f, max %f' %(f_min,f_max))
        f_avg = sum(f,axis=0)/sz
        if f_avg == 0.:
            e = np.ones_like(f)
        else:
            if pop.min_or_max() == 'max':
                e = f/f_avg
            else:
                e = (-f+f_max+f_min)/f_avg
        self.expected_value = e
        garauntee,chance = divmod(e,1.)
#               garauntee = floor(e)
#               chance = remainder(e,1)
        choices = []
        for i in xrange(sz):
            choices = choices + [pop[i]] * int(garauntee[i])
        #now deal with the remainder
        dart_board = np.add.accumulate(chance / sum(chance,axis=0))
        for i in range(len(choices),sz):
            dart = prng.random()
            idx = 0
            while dart > dart_board[idx]:
                idx = idx + 1
            choices.append(pop[idx])
        self.choices = choices

    def select(self,pop,cnt = 1): #ignore the past in pop
        res = []
        for i in range(cnt):
            res.append(prng.choice(self.choices))
#               for chosen in res: self.choices.remove(chosen)
        if cnt == 1:
            return res[0]
        return res

    def clear(self):
        if hasattr(self,'choices'):
            del self.choices
