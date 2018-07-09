## Instructions to Run

System Used: Windows 10, 64 bit
PostgreSQL version = 9.6.2
Python version = 3.6.5

Create a virtual environment for the project and import the db into Postgres:
	$ virtualenv venv
	$ .\venv\Scripts\activate
	
	###### Install the required packages from the file
	$ pip install < requirements.txt
	
	###### Talking to Postgres:
	###### create a db
	$ createdb pluralsight
	###### import the sql file to postgres db
	$ psql -U username pluralsight < pluralsight.sql
	
	Edit the Server.py:
		Edit the create_engine() to add your postgres credentials.
		Check the server.py file
	Run the python file:
	$ python server.py
	
	Copy: http://127.0.0.1:5431/user_similarity/<user_handle>
	eg: http://127.0.0.1:5431/user_similarity/45
