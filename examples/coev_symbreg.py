#    This file is part of DEAP.
#
#    DEAP is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of
#    the License, or (at your option) any later version.
#
#    DEAP is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with DEAP. If not, see <http://www.gnu.org/licenses/>.

import random

from deap import base
from deap import creator
from deap import gp
from deap import tools

# gp_symbreg already defines some useful structures
import gp_symbreg

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("IndGA", list, fitness=creator.FitnessMax)

def refFunc(x):
    return x**4 + x**3 + x**2 + x
    
def evalSymbReg(expr, data):
    # Transform the tree expression in a callable function
    func = tools_gp.lambdify(expr=expr)
    # Evaluate the sum of squared difference between the expression
    # and the real function : x**4 + x**3 + x**2 + x
    values = data
    diff_func = lambda x: (func(x)-refFunc(x))**2
    diff = sum(map(diff_func, values))
    return diff,

toolbox_ga = base.Toolbox()

toolbox_ga.register("float", random.uniform, -1, 1)
toolbox_ga.register("individual", tools.initRepeat, creator.IndGA, toolbox_ga.float, 10)
toolbox_ga.register("population", tools.initRepeat, list, toolbox_ga.individual)

toolbox_ga.register("select", tools.selTournament, tournsize=3)
toolbox_ga.register("mate", tools.cxTwoPoints)
toolbox_ga.register("mutate", tools.mutGaussian, mu=0, sigma=0.01, indpb=0.05)

tools_gp = gp_symbreg.toolbox

def main():
    pop_ga = toolbox_ga.population(n=200)
    pop_gp = tools_gp.population(n=200)
    
    stats_ga = tools.Statistics(lambda ind: ind.fitness.values)
    stats_ga.register("Avg", tools.mean)
    stats_ga.register("Std", tools.std)
    stats_ga.register("Min", min)
    stats_ga.register("Max", max)
    
    stats_gp = tools.Statistics(lambda ind: ind.fitness.values)
    stats_gp.register("Avg", tools.mean)
    stats_gp.register("Std", tools.std)
    stats_gp.register("Min", min)
    stats_gp.register("Max", max)
    
    best_ga = tools.selRandom(pop_ga, 1)[0]
    best_gp = tools.selRandom(pop_gp, 1)[0]
    
    for ind in pop_gp:
        ind.fitness.values = evalSymbReg(ind, best_ga)  
    
    for ind in pop_ga:
        ind.fitness.values = evalSymbReg(best_gp, ind)
    
    CXPB, MUTPB, NGEN = 0.5, 0.2, 50
    
    # Begin the evolution
    for g in range(NGEN):
        print "-- Generation %i --" % g
    
        # Select and clone the offsprings
        off_ga = toolbox_ga.select(pop_ga, len(pop_ga))
        off_gp = tools_gp.select(pop_gp, len(pop_gp))
        off_ga = [toolbox_ga.clone(ind) for ind in off_ga]        
        off_gp = [tools_gp.clone(ind) for ind in off_gp]
    
    
        # Apply crossover and mutation
        for ind1, ind2 in zip(off_ga[::2], off_ga[1::2]):
            if random.random() < CXPB:
                toolbox_ga.mate(ind1, ind2)
                del ind1.fitness.values
                del ind2.fitness.values
    
        for ind1, ind2 in zip(off_gp[::2], off_gp[1::2]):
            if random.random() < CXPB:
                tools_gp.mate(ind1, ind2)
                del ind1.fitness.values
                del ind2.fitness.values
    
        for ind in off_ga:
            if random.random() < MUTPB:
                toolbox_ga.mutate(ind)
                del ind.fitness.values
    
        for ind in off_gp:
            if random.random() < MUTPB:
                tools_gp.mutate(ind)
                del ind.fitness.values
    
        # Evaluate the individuals with an invalid fitness     
        for ind in off_ga:
            if not ind.fitness.valid:
               ind.fitness.values = evalSymbReg(best_gp, ind)
        
        for ind in off_gp:
            if not ind.fitness.valid:
                ind.fitness.values = evalSymbReg(ind, best_ga)
                
        # Replace the old population by the offsprings
        pop_ga = off_ga
        pop_gp = off_gp
        
        stats_ga.update(pop_ga)
        stats_gp.update(pop_gp)
        
        best_ga = tools.selBest(pop_ga, 1)[0]
        best_gp = tools.selBest(pop_gp, 1)[0]    
    
        print "  -- GA statistics --"
        print "  Min %s" % stats_ga.Min[0][-1][0]
        print "  Max %s" % stats_ga.Max[0][-1][0]
        print "  Avg %s" % stats_ga.Avg[0][-1][0]
        print "  Std %s" % stats_ga.Std[0][-1][0]
        print "  -- GP statistics --"        
        print "  Min %s" % stats_gp.Min[0][-1][0]
        print "  Max %s" % stats_gp.Max[0][-1][0]
        print "  Avg %s" % stats_gp.Avg[0][-1][0]
        print "  Std %s" % stats_gp.Std[0][-1][0]

    print "Best individual GA is %s, %s" % (best_ga, best_ga.fitness.values)
    print "Best individual GP is %s, %s" % (gp.evaluate(best_gp), best_gp.fitness.values)

    return pop_ga, pop_gp, stats_ga, stats_gp, best_ga, best_gp

if __name__ == "__main__":
    main()
