'''
CS 3700 - Networking & Distributed Computing - Fall 2024
Instructor: Thyago Mota
Student(s): Kevin O'Connell
Description: Project 3 - Bitcoin Simulation
'''

import time
import sys
import stomp
import json
import threading
import hashlib
import random
import os


# TODO: change STUDENT_ID, BROKER_USER, and BROKER_PASSWD
STUDENT_ID = 'koconn48'
TASKS_TOPIC = f'/topic/bitcoin/{STUDENT_ID}_tasks'
SOLUTIONS_TOPIC = f'/topic/bitcoin/{STUDENT_ID}_solutions'
BROKER_ENDPOINT = '24fcs3700.msudenver.edu'
BROKER_PORT = 61613
BROKER_USER = '1234'
BROKER_PASSWD = '4321'

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
    full_path = os.path.abspath(file_name)
    print(f"[Debug] Attempting to save solution to {full_path}: {solution}")
    try:
        with open(file_name, 'at') as f:
            print(f"[Debug] Opened file {full_path} for writing.")
            for value in solution['task']['data']:
                f.write(f'{value} ')
            f.write(f", {solution['task']['zeros']}, ")
            for value in solution['nonce']:
                f.write(f'{value} ')
            f.write('\n')
            print(f"[Debug] Successfully wrote to file {full_path}.")
    except FileNotFoundError as e:
        print(f"[Error] FileNotFoundError: {e}")
    except PermissionError as e:
        print(f"[Error] PermissionError: {e}")
    except Exception as e:
        print(f"[Error] Unexpected error while saving solution: {e}")

# determine whether the given digest has the expected number of zeros required by the task
def is_solved(task, digest):
    for i in range(task['zeros']):
        if digest[i] != 0:
            return False
    return True

# TODO: attempt to find a solution to a given task by generating random nonces; announce the solution found; quit execution when a solution found (either by itself or some other bitcoin miner)
def mine(conn, id, task):
    print(f"[Miner {id}] Working on task: {task}")
    global solution_found
    while not solution_found:
        nonce = [random.randint(0, 255) for _ in range(4)]
        hash_function = hashlib.md5()
        data = bytearray(task['data'] + nonce)
        hash_function.update(data)
        digest = hash_function.digest()
        if is_solved(task, digest):
            semaphore.acquire()
            if not solution_found:
                solution_found = True
                solution = {'task': task, 'nonce': nonce}
                print(f"[Miner {id}] Preparing to publish solution: {solution}")
                try:
                    conn.send(body=json.dumps(solution), destination=SOLUTIONS_TOPIC)
                    print(f"[Miner {id}] Published solution to {SOLUTIONS_TOPIC}: {solution}")
                except Exception as e:
                    print(f"[Miner {id}] Failed to publish solution: {e}")
            semaphore.release()

# TODO: finish the implementation of the tasks listener
class TasksListener(stomp.ConnectionListener):
    def __init__(self, conn, id):
        super().__init__()
        self.conn = conn
        self.id = id
        print(f"[Miner {self.id}] Listening on {TASKS_TOPIC}")

    def on_message(self, frame):
        global solution_found
        solution_found = False
        task = json.loads(frame.body)
        print(f"[Miner {self.id}] Received task: {task}")
        mine(self.conn, self.id, task)

# TODO: finish the implementation of the solutions listener
class SolutionsListener(stomp.ConnectionListener):
    def __init__(self, conn, role):
        super().__init__()
        self.conn = conn
        self.role = role  # 'main' or 'miner'
        print(f"[{self.role}] Listening on {SOLUTIONS_TOPIC}")

    def on_message(self, frame):
        print(f"[{self.role}] Raw frame received: {frame.body}")
        global solution_found
        solution = json.loads(frame.body)
        print(f"[{self.role}] Solution received: {solution}")
        semaphore.acquire()
        solution_found = True
        semaphore.release()
        if self.role == 'main':
            ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
            output_file = os.path.join(ROOT_DIR, 'data/output.txt')
            print(f"[Debug] Using output file path: {output_file}")
            save_solution(output_file, solution)
            print(f"[{self.role}] Solution saved to output.txt")
            if tasks:
                task = tasks.pop()
                self.conn.send(body=json.dumps(task), destination=TASKS_TOPIC)
                print(f"[Main] Published next task: {task}")


if __name__ == '__main__':
    # validate parameters
    if len(sys.argv) not in [2, 3]:
        print(f'Usage: {sys.argv[0]} m|b id, where m=main, b=miner, id=miner_id')
        sys.exit(1)

    role_arg = sys.argv[1].lower()
    if role_arg not in ['m', 'b']:
        print('Unknown role!')
        sys.exit(1)

    role = 'main' if role_arg == 'm' else 'miner'
    id = 'main' if role_arg == 'm' else f'miner #{sys.argv[2]}'
    print(f"[{id}] Starting...")

    print(f"[Debug] Current working directory: {os.getcwd()}")

# create the connections to message broker
    conn_tasks = stomp.Connection([(BROKER_ENDPOINT, BROKER_PORT)])
    conn_solutions = stomp.Connection([(BROKER_ENDPOINT, BROKER_PORT)])

    try:
        conn_tasks.connect(BROKER_USER, BROKER_PASSWD, wait=True)
        conn_solutions.connect(BROKER_USER, BROKER_PASSWD, wait=True)
        print(f"[{id}] Connected to broker.")
    except Exception as e:
        print(f"[{id}] Failed to connect: {e}")
        sys.exit(1)

    # TODO: set the solutions listener, disregarding of role
    conn_solutions.set_listener('', SolutionsListener(conn_solutions, role))
    conn_solutions.subscribe(destination=SOLUTIONS_TOPIC, id=1, ack='auto')  # Subscribe to solutions topic
    print(f"[{id}] Subscribed to solutions topic {SOLUTIONS_TOPIC}")

# TODO: have main create and publicize the first task
    if role == 'main':
        global tasks
        tasks = load_tasks('data/input.txt')
        if tasks:
            task = tasks.pop()
            conn_tasks.send(body=json.dumps(task), destination=TASKS_TOPIC)
            print(f"[Main] Published initial task: {task}")
 # TODO: set the tasks listener only if the role is miner            
    elif role == 'miner':
        conn_tasks.set_listener('', TasksListener(conn_tasks, id))
        conn_tasks.subscribe(destination=TASKS_TOPIC, id=1, ack='auto')  # Ensure subscription
        print(f"[Miner {id}] Subscribed to task queue.")

 # loop forever to avoid the main thread to end
    while True:
        time.sleep(1)
