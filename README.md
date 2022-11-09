# AddressBookApp
An address book application created using FastAPI framework where users can create, read, update and delete addresses .The addresses are stored in SQLite database. Also, users can fetch the addresses that are within a given distance and location coordinates.

# Commands to execute:
pip install -r requirements.txt

uvicorn main:app --reload

Note: After running the server via the above-mentioned command i.e., uvicorn main:app --reload, open a browser and type the below URL so that all the created API will be shown and testing can be done for each of them:

http://127.0.0.1:8000/docs
