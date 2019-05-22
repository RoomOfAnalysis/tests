#!/usr/bin/env python3
"""
@author:Harold
@file: threadpoolexecutor_in_processpoolexecutor.py
@time: 22/05/2019
"""

# reference: https://stackoverflow.com/questions/19994478/a-threadpoolexecutor-inside-a-processpoolexecutor

from concurrent import futures
import time


MAX_PROCESSES = 3
MAX_THREADS = 2
CHUNKSIZE = 100


class Particle:
    def __init__(self, i):
        self.i = i
        self.fitness = None

    def get_fitness(self):
        self.fitness = 2 * self.i


def thread_worker(p):
    p.get_fitness()
    return p.i, p


def proc_worker(ps):
    with futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as e:
        result = list(e.map(thread_worker, ps))
    return result


def update_fitness(particles):
    with futures.ProcessPoolExecutor(max_workers=MAX_PROCESSES) as e:
        for result_list in e.map(
            proc_worker,
            (particles[i: i + CHUNKSIZE] for i in range(0, len(particles), CHUNKSIZE)),
        ):
            for i, p in result_list:
                particles[i] = p


def update_fitness_thread_only(particles):
    result = proc_worker(particles)
    for i, p in result:
        particles[i] = p


if __name__ == "__main__":
    particles = [Particle(i) for i in range(500000)]
    assert all(particles[i].i == i for i in range(len(particles)))

    start = time.time()
    # update_fitness(particles)  # time consumption:  6.055685520172119
    update_fitness_thread_only(particles) # time consumption:  27.56034278869629
    print("time consumption: ", time.time() - start)

    assert all(particles[i].i == i for i in range(len(particles)))
    assert all(p.fitness == 2 * p.i for p in particles)
