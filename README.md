# health-app
This app store some health measurement to a mongo database.
It is written in django and use django rest framework.

To run the app, docker must be installed in the computer. Then run the commands as follows:

docker buld . -t healthapp
docker-compose up

Example of requests:
To get observations of a monitored person (The monitored is a int and it is in the URL)
````
curl --location --request GET 'http://localhost:8000/monitored/456/observations?observation_name=blood_pressure'

````

To get the mean:
````
curl --location --request GET 'http://localhost:8000/observations?observation_name=temperature&aggregator=mean'
````

Example of posting
````
curl --location --request POST 'http://localhost:8000/observations' \
--header 'Content-Type: application/json' \
--data-raw '{
"monitored_id": 123,
"observation_name": "temperature",
"issued": "2022-02-21T08:20:01.52+01:00",
"value": "36.0",
"value_type": "float",
"value_units": "celsius"
}'
````
