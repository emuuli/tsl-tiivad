# Setup
* Use Python 3.10
* Install requirements from requirements.txt

# Run validation
```

```

# Running tests:
```
# All tests
python -m pytest
# For one file
python -m pytest test/test_file.py
```

# Packaging:
* Remove the old versions from `dist` folder.
* Change the version in `tiivad/version.py` and run:
```
python setup.py sdist
```

##  Let's upload the new version:
```
python -m twine upload dist/* 

user: __token__
pwd: <token>
```

## PyPi repo asukoht:
https://pypi.org/project/tiivad/

# Local run/test with Docker
## Update the tiivad-base version in tiivad-base file
```
# File to change in: tsl-tiivad/docker/tiivad-base
RUN pip3 install --no-cache-dir tiivad==0.0.30[requirements.txt](..%2F..%2FDesktop%2FEerik%2Ftsl-tiivad%2Frequirements.txt)
```

## Let's rename the image with -t .
```
cd ..
cd docker
docker build --progress plain --no-cache -f tiivad-base -t tiivadbase1 .
```

## Let's build the second container with assessment code and sample solution
```
docker build --progress plain --no-cache -f dockerfile-evaluate -t evaluate1 .
```

## Get docker images
```
docker images
```

## Run the latest evaluate container and name it "evaluator"
```
docker run -it --name evaluator evaluate1 /bin/bash
```

### Inside the container run:
```
./evaluate.sh
```

## Print the logs (outside the container, another terminal)
```
docker logs evaluator
```
