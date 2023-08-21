# -*- coding: utf-8 -*-
"""
Created on Thu Aug  3 20:06:25 2023

@author: hongyu
"""

from langchain import PromptTemplate

input_prompt = PromptTemplate(input_variables = ["goal", "function","constraint"], template = "goal:{goal}\nfunction:{function}\nconstraint:{constraint}\n")
goal = input('input goal:')
function = input('input function:')
constraint = input('input constraint')
prompt = input_prompt.format(goal = goal, function = function, constraint = constraint)
print(prompt)
