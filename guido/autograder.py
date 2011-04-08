#!/usr/bin/env python3

"""
This script parses and adds the autograder output into the Guido
database.

The format is assumed to be in the following style:

<problem number>.<optional subnumbers>: <problem-name>: <result>
      <result specifics....>

The script parses each output between this form, records a pass or
fail, and enters that information into the database. It also saves the
compelte autograder output just in case it is needed.
"""

import sys
import re
import subprocess

def runtests(assignment, path):
    """Runs the autograder on an assignment and path and returns the
    output"""
    cmd = ("mgrade %s %s" % (assignment, path))
    
    output = subprocess.getoutput(cmd)
    return output

def build(grader_output):
    """Returns a list of autograder outputs, organized by
    problem. Each problem's output is a tuple that contains the
    problem number, the name of the problem, the result (failed or
    passed), and any extra specifics the autograder outputted (test
    cases, for example)"""
    lines = grader_output.splitlines(True)
    l = len(lines)

    del lines[0:2] #removes the greeting
    del lines[l-6:l] #removes the final test results

    pat = re.compile("(\d.*): (.*): (.*)") 

    #these are the values in which we are interested for each
    #problem's autograder output
    built_output = []
    number = None
    name = None
    result = None
    specifics = ''
    getting_specifics = 0

    #for each line in lines, build the problem's output
    for line in lines:
        ids = pat.match(line)
        if ids:
            #if we were getting specifics, we are done now.
            if(getting_specifics == 1):
                getting_specifics = 0
                grader_problem = (number, name, result, specifics)
                built_output.append(grader_problem)

            #parse ids
            number = ids.group(1)
            name = ids.group(2)
            result = ids.group(3)

        else: #else we are getting specifics
            if(line == '\n'):
                line = '' #we dont want rogue newlines
            if(getting_specifics == 1):
                specifics += line 
            else:
                specifics = line 
                getting_specifics = 1

    #finally, make sure to add the last one that was built.
    grader_problem = (number, name, result, specifics)
    built_output.append(grader_problem)
    return built_output


def get_autograder_results(assignment, path):
    """Function that you should call. Takes an assignment ID and a path for a
    student solution to that assignment. Returns a dictionary from problem IDs
    to the autograder output for that problem."""
    output = runtests(assignment, path)
    return build(output)


def fake_autograder_results(assignment, path):
    """Returns some fake autograder results"""
    return build("Results for Assignment 10\n\n2: insert: FAILED \n  Test:     (insert < 6 '(1 3 5 7 9 11))\n   Expected: (1 3 5 6 7 9 11)\n   Actual:   (6 1 3 5 7 9 11)\n\n5.b: list-bst: FAILED\n   Test:  (list->bst > '())\n   Error: Exception in car: () is not a pair\n\n6.a: sort-by-weight: FAILED\n   Test:  (sort-by-weight\n  '((#\A 8) (#\B 7) (#\C 1) (#\D 2) (#\E 3) (#\F 4) (#\G 5)\n   Error: Probable Infinite Loop\n\nTest Results\n   Passed: 6.\n   Failed: 3. \n   Missing: 0. \n")
           
