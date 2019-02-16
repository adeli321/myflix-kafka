echo Stopping Services
sudo docker stop pyvideo
sudo docker stop pylogin
sudo docker stop pyregister

sudo docker rm pyvideo
sudo docker rm pylogin
sudo docker rm pyregister

sudo docker build -f Dockerfile-1 -t pyvideo .
sudo docker build -f Dockerfile-2 -t pylogin .
sudo docker build -f Dockerfile-3 -t pyregister .

sudo docker run -d -it -p 8080:8080 --name pyvideo pyvideo 
sudo docker exec -d pyvideo python3 video.py

sudo docker run -d -it --name pylogin pylogin
sudo docker exec -d pylogin python3 postgres_login.py

sudo docker run -d -it --name pyregister pyregister
sudo docker exec -d pyregister python3 postgres_register.py
