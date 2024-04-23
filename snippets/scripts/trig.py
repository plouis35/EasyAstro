#!/usr/bin/python3

import math

# Print something for the user

print('I will find trigometric functions for an angle.\n')


# Ask for a value for the angle

angle = input('What is the angle in degrees? >> ')
a = float(angle)
arad = math.radians(a)
sine = math.sin(arad)
cosine = math.cos(arad)
tangent = math.tan(arad)
print('\n')
print('Radians: ', arad)
print('Sine: ', sine)
print('Cosine: ', cosine)
print('Tangent: ', tangent)
print('\n')
exit()
