'''
CS 3700 - Networking & Distributed Computing - Fall 2024
Instructor: Thyago Mota
Student:
Description: Project 3 - Hashing
'''

import hashlib

class HashMain:
    def __init__(self):
        self.hash_function = hashlib.md5()

    def hash(self, data):
        self.hash_function.update(data.encode('utf-8'))
        return self.hash_function.hexdigest()

if __name__ == "__main__":
    hash_main = HashMain()
    examples = ["Computer Science", "Computer SciencE", "Bitcoin"]
    for example in examples:
        print(f'Hash value of "{example}" is "{hash_main.hash(example)}"')
