'''
CS 3700 - Networking & Distributed Computing - Fall 2024
Instructor: Thyago Mota
Student(s):
Description: Project 3 - Bitcoin Test
'''

import unittest
import hashlib

class BitcoinTestCase(unittest.TestCase): 

    def load_solutions(file_name): 
        with open(file_name, 'rt') as f: 
            solutions = []
            for line in f: 
                line = line.strip()
                data = line.split(',')
                solution = {}
                solution['data'] = [int(value) for value in data[0].split()]
                solution['zeros'] = int(data[1])
                solution['nonce'] = [int(value) for value in data[2].split()]
                solutions.append(solution)
            print(f'{len(solutions)} solutions loaded!')
            return solutions

    def is_solved(solution, digest): 
        for i in range(solution['zeros']):
            if digest[i] != 0:
                return False 
        return True
    
    def test_bitcoin(self):
        solutions = BitcoinTestCase.load_solutions('data/output.txt')
        for solution in solutions: 
            hash_function = hashlib.md5()
            data = bytearray(solution['data'] + solution['nonce'])
            hash_function.update(data)
            digest = hash_function.digest()
            self.assertTrue(BitcoinTestCase.is_solved(solution, digest))

if __name__ == '__main__':
    unittest.main()
