from datetime import *
from hashlib import blake2b
from time import *
from models import *
from flask import *


countries = [['Italy',5],['Germany',2],['Greece',4]]
for c in countries:
    print(c[0],c[1])
    
#jsonify(countries)
#jsonify(cntrs=[{'Paese':c[0],'Ascoltatori':c[1]} for c in countries])
print(json.dumps(countries))


l=[]

for c in countries:
    dict={}
    dict['Paese'] = c[0]
    dict['Ascoltatori'] = c[1]
    l.append(dict)
#jsonify(l)
print(json.dumps(l))

