## To build the image
```sh
docker build -t das-img .
```
It should take a few minutes to build and image size is ~2GB
## Run the image
```sh
docker run --name das-container -p 3000:3000 -p 8000:8000 das-img
```
To access it go to [port 3000](http://127.0.0.1:3000)