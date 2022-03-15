## Development

`docker-compose up --build`

### Run Tests

`docker-compose -f docker-compose.yml -f docker-compose.test.yml up --build --abort-on-container-exit`

## Active venv

`source ./venv/bin/activate`

## Download requirements

`pip install -r requirements.txt`

## Test

`pytest`