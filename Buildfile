echo Stopping Services
sudo docker stop pyvideo
sudo docker stop pylogin
sudo docker stop pyregister
sudo docker stop pycreditcheck
sudo docker stop pycreditinsert

echo Removing Services
sudo docker rm pyvideo
sudo docker rm pylogin
sudo docker rm pyregister
sudo docker rm pycreditcheck
sudo docker rm pycreditinsert

echo Building Services
sudo docker build -t pyvideo -f Dockerfile-1 .
sudo docker build -t pylogin -f Dockerfile-2 .
sudo docker build -t pyregister -f Dockerfile-3 .
sudo docker build -t pycreditcheck -f Dockerfile-4 .
sudo docker build -t pycreditinsert -f Dockerfile-5 .

echo Running Services
sudo docker run -d -it -p 8080:8080 --name pyvideo pyvideo 
sudo docker exec -d pyvideo python3 video.py

sudo docker run -d -it --name pylogin pylogin
sudo docker exec -d pylogin python3 postgres_login.py

sudo docker run -d -it --name pyregister pyregister
sudo docker exec -d pyregister python3 postgres_register.py

sudo docker run -d -it --name pycreditcheck pycreditcheck 
sudo docker exec -d pycreditcheck python3 credit_check.py

sudo docker run -d -it --name pycreditinsert pycreditinsert
sudo docker exec -d pycreditinsert python3 credit_insert.py
