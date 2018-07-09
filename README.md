## Instructions to Run

System Used: Windows 10, 64 bit <br/>
PostgreSQL version = 9.6.2 <br/>
Python version = 3.6.5 <br/>

### Create a virtual environment for the project and import the db into PostgreSQL, Edit and run the python file:
	$ virtualenv venv
	$ .\venv\Scripts\activate
	
	###### Install the required packages from the file
	$ pip install < installations.txt
	
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
	
	Copy and paste the link on the browser: 
		http://127.0.0.1:5431/user_similarity/<user_handle>
	Example (Will provide the user similarities for user_handle=45): 
		http://127.0.0.1:5431/user_similarity/45
	