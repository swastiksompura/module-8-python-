# Q13. Write a Python program to match a word in a string using re.match(). 

import re

# Input string
text = "Python is fun to learn."

# Word to match
word = "Python"

# Match using re.match()
match = re.match(word, text)

if match:
    print(f" Word '{word}' matched at the beginning of the string.")
else:
    print(f" Word '{word}' not found at the beginning.")
