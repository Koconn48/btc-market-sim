'''
CS 3700 - Networking & Distributed Computing - Fall 2024
Instructor: Thyago Mota
Student(s):
Description: Project 3 - Bitcoin Simulation
'''

import time
import sys
import stomp
import json
import threading
import hashlib
import random

# TODO: change STUDENT_ID, BROKER_USER, and BROKER_PASSWD
STUDENT_ID      = 'tmota'
TASKS_TOPIC     = f'/topic/bitcoin/{STUDENT_ID}_tasks'
SOLUTIONS_TOPIC = f'/topic/bitcoin/{STUDENT_ID}_solutions'
BROKER_ENDPOINT = '24fcs3700.msudenver.edu'
BROKER_PORT     = 61613
BROKER_USER     = '***'
BROKER_PASSWD   = '***'

# solution_found is updated by multiple threads (hence the need of a semaphore)
semaphore = threading.Semaphore(1)
solution_found = False 

# return alls tasks read from a given file name and path
# tasks = [{ 'data': [byte, ...], 'zeros': int }, ...]
def load_tasks(file_name): 
    with open(file_name, 'rt') as f: 
        tasks = []
        for line in f: 
            line = line.strip()
            data = line.split(',')
            task = {}
            task['data'] = [int(value) for value in data[0].split()]
            task['zeros'] = int(data[1])
            tasks.append(task)
        print(f'{len(tasks)} tasks loaded!')
        return list(reversed(tasks))
    
# append the given solution into the given file name and path
# solution = {'data': [byte, ...], 'zeros': int, 'nonce': [byte, ...]}
def save_solution(file_name, solution): 
    with open(file_name, 'at') as f: 
        for value in solution['data']:
            f.write(f'{value} ')
        f.write(f", {solution['zeros']}, ")
        for value in solution['nonce']:
            f.write(f'{value} ')
        f.write('\n')

# determine whether the given digest has the expected number of zeros required by the task
def is_solved(task, digest): 
    for i in range(task['zeros']):
        if digest[i] != 0:
            return False 
    return True

# TODO: attempt to find a solution to a given task by generating random nonces; announce the solution found; quit execution when a solution found (either by itself or some other bitcoin miner)
def mine(conn, id, task):
    print(f'-> working on {task}')
    global solution_found
    while not solution_found: 
        pass

# TODO: finish the implementation of the tasks listener
class TasksListener(stomp.ConnectionListener):

    def __init__(self, conn, id): 
        super().__init__()
        self.conn = conn
        self.id = id

    def on_message(self, frame):
        pass

# TODO: finish the implementation of the solutions listener
class SolutionsListener(stomp.ConnectionListener):

    def __init__(self, conn, role): 
        super().__init__()
        self.conn = conn
        self.role = role

    def on_message(self, frame):
        pass

if __name__ == '__main__':

    # validate parameters
    if len(sys.argv) not in [2, 3]: 
        print(f'Use {sys.argv[0]} m|b id, where m=main, b=bitcoin miner, and id identifies the miner')
        sys.exit(1)
    role = sys.argv[1].lower()
    if role not in ['m', 'b']:
        print('Unkown role!')
        sys.exit(1)
    print(f"Role is {'main' if role == 'm' else 'bicoin miner'}")
    id = 'main'
    if role == 'b':
        id = f'miner #{sys.argv[2]}'
    print(f'Id is {id}')

    # create the connections to message broker
    conn_tasks = stomp.Connection([(BROKER_ENDPOINT, BROKER_PORT)]) 
    conn_solutions = stomp.Connection([(BROKER_ENDPOINT, BROKER_PORT)]) 
    print('Trying to connect to message broker...')
    conn_tasks.connect(BROKER_USER, BROKER_PASSWD, wait=True)
    conn_solutions.connect(BROKER_USER, BROKER_PASSWD, wait=True)
    print('Success!')

    # TODO: set the solutions listener, disregarding of role 
    pass

    # TODO: have main create and publicize the first task
    if role == 'm':
        global tasks
        tasks = load_tasks('data/input.txt')
        pass

    # TODO: set the tasks listener only if the role is miner
    if role == 'b':   
        pass

    # loop forever to avoid the main thread to end
    while True: 
        time.sleep(1)
