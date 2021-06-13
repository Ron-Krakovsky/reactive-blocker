
from bitarray import bitarray

def bitfield(n):
    return [int(digit) for digit in bin(n)[2:]]

intnumber = 320

bitnumber = bitarray(bitfield(intnumber))
count = 9 - len(bitnumber)
for j in range(9-len(bitnumber)):
    bitnumber.append(False)
if count != 0:
    bitnumber2 = (bitarray('0') * count) + bitnumber[:-count]
else:
    bitnumber2 = bitnumber
y = bitarray('000000000')
for i in range(9):
    y[8-i] = bitnumber2[i]
print(int(y.to01(), 2))

