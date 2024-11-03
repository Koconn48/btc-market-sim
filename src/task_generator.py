'''
CS 3700 - Networking & Distributed Computing - Fall 2024
Instructor: Thyago Mota
Student(s):
Description: Project 3 - Bitcoin Simulation (task generator)
'''

import random 

TASK_SIZES = [ 1, 1, 1, 1, 2, 2, 2, 3, 3, 4]

if __name__ == '__main__':
    with open('data/input.txt', 'wt') as f: 
        for task_size in TASK_SIZES:
            for _ in range(32):
                f.write(f'{random.randint(0, 255)} ') 
            f.write(f', {task_size}\n')
