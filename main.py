from sqlalchemy.orm import Session
import models
from database import SessionLocal, engine
from fastapi import Depends, FastAPI, HTTPException
from math import radians, cos, sin, asin, sqrt, floor

def get_db():
    '''
    Creates database instance for each request and stores in session
    '''
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Populating tables in database
models.Base.metadata.create_all(bind=engine)

# Creating an instance of FastAPI class which is used to create app
app = FastAPI()

def validate_coordinates(latitude,longitude):
    '''
    This function validates the latitude and longitude entered by the user.
    Parameter: latitude(float),longitude(float).
    Return: error message if any(string).
    ''' 
    msg = ""
    if latitude not in range(-90,91):
        msg += "Please enter valid latitude (-90 to 90 degree)"
    if longitude not in range(-180,181):
        if msg:
            msg += " and Please enter valid longitude (-180 to 180 degree)"
        else:
            msg += "Please enter valid longitude (-180 to 180 degree)"
    return msg

def filter_valid_address(lat1, long1, all_address, distance):
    '''
    This function calculates the distance between coordinates entered by the user with all the coordinates available in the table and then compares it with the entered 
    threshold distance.
    Parameter: latitude(float),longitude(float),list of coordinates from database(list), distance(float).
    Return: list of valid coordinates(list).
    ''' 
    lat1 = radians(lat1)
    long1 = radians(long1)
    valid_coordinates = []
    for address in all_address:        
        lat2 = radians(address.latitude)
        long2 = radians(address.longitude)

        # Haversine formula
        dlon = long2 - long1
        dlat = lat2 - lat1
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * asin(sqrt(a))
        
        # Radius of earth in kilometers
        r = 6371
        curr_dist = c * r
        
        # calculate the result
        if curr_dist <= distance:
            valid_coordinates.append({"Latitude":address.latitude,"Longitude":address.longitude})
    return valid_coordinates

@app.post('/address/create')
async def create_address(latitude_in_degree:float, longitude_in_degree:float, db: Session = Depends(get_db)):
    '''
    This function creates address based the latitude and longitude in degree entered by the user post validation.
    Parameter: latitude(float),longitude(float).
    Return: Json Response.
    ''' 
    error_msg = validate_coordinates(latitude_in_degree, longitude_in_degree)
    if not error_msg:
        new_address = models.Address(latitude=latitude_in_degree, longitude=longitude_in_degree)
        db.add(new_address)
        db.commit()
        return {"message":"New address created successfully!"}
    else:
        raise HTTPException(status_code=400, detail=error_msg)

@app.post('/address/read/{id}')
async def read_address(id: int, db: Session = Depends(get_db)):
    '''
    This function fetches address based on the id entered by the user.
    Parameter: id(int).
    Return: latitude(float),longitude(float) if found.
    ''' 
    existingAddress = db.query(models.Address).get(id)
    if existingAddress:
        return {"latitude":existingAddress.latitude, "longitude":existingAddress.longitude}
    else:
        raise HTTPException(status_code=404, detail="Address not found!")

@app.post('/address/update/{id}')
async def update_address(id: int, new_latitude_in_degree:float, new_longitude_in_degree:float, db: Session = Depends(get_db)):
    '''
    This function updates address in database based on the latitude and longitude in degree entered by the user post validation.
    Parameter: id(int), latitude(float), longitude(float).
    Return: Json Response.
    ''' 
    error_msg = validate_coordinates(new_latitude_in_degree, new_longitude_in_degree)
    if not error_msg:
        existingAddress = db.query(models.Address).get(id)
        # update todo item with the given task (if an item with the given id was found)
        if existingAddress:
            existingAddress.latitude=new_latitude_in_degree
            existingAddress.longitude=new_longitude_in_degree
            db.commit()
            return {"message":"Address updated successfully!"}
        else:
            raise HTTPException(status_code=404, detail="Address not found!")
    else:
        raise HTTPException(status_code=400, detail=error_msg)

@app.post('/address/delete/{id}')
async def delete_address(id: int, db: Session = Depends(get_db)):
    '''
    This function deletes address based on the id entered by the user if found.
    Parameter: id(int).
    Return: Json Response.
    ''' 
    existingAddress = db.query(models.Address).get(id)
    if existingAddress:
        temp_address = existingAddress
        db.delete(existingAddress)
        db.commit()
        return {"Deleted Address":temp_address}
    else:
        raise HTTPException(status_code=404, detail="Address not found!")

@app.post('/address/retrieve/')
async def retrieve_address(latitude_in_degree:float, longitude_in_degree:float, distance_in_km:float, db: Session = Depends(get_db)):
    '''
    This function retrieves all the valid address from database based on the user provided distance and location coordinates.
    Parameter: latitude(float),longitude(float), distance(float).
    Return: list of valid coordinates(list of dictionaries) if found.
    ''' 
    error_msg = validate_coordinates(latitude_in_degree, longitude_in_degree)
    if not error_msg:
        all_address = db.query(models.Address).all()
        if all_address:
            result = filter_valid_address(latitude_in_degree,longitude_in_degree,all_address,distance_in_km)
            if result:
                return {"Result":result}
            else:
                return {"message":"No coordinates found within the given distance and location coordinates!"}
        else:
            return {"message":"No coordinates found in the table. Please add few and retry!"}
    else:
        raise HTTPException(status_code=400, detail=error_msg)
