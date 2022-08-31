from datetime import *
from time import *
from models import *
from flask import *

users_like_me=session.query(Users).all()
        
medium_age = 0
for x in users_like_me:
    medium_age += 2022-x.BirthDate.year
medium_age /= len(users_like_me)
medium_age = int(medium_age)
print(int(medium_age))

countries = session.query(Users.Country,func.count(Users.Email)).group_by(Users.Country).all()
for c in countries:
    print(c[0],c[1])
    
print(jsonify(countries))