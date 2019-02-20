# myflixKafka
Video Streaming service utilizing Kafka for login functionality

To run this video streaming service, 6 gcloud instances are required. Each one has a specific use:
Kafka - provides the kafka broker to manage the login, register, credit-check, and credit-insert services
MongoDB - provides video storage
MongoDB - provides video storage for additional videos
PostgreSQL - provides SQL database for login, register, credit-check, and credit-insert services
Jenkins - provides automated build setup to launch when the dev branch of myflixKafka repo is updated
Ubuntu/python - instance which has a container that runs 5 services in 5 python containers: the flask app providing 
the front-end, login, register, credit-check, and credit-insert services

TO launch the kafka service:
  1. spin up a gcloud instance (container-optimised or coreos)
  2. create an alias to run the docker-compose command
    a. ```alias docker-compose='docker run --rm \ 
    -v /var/run/docker.sock:/var/run/docker.sock \ 
    -v "$PWD:/rootfs/$PWD" \ 
    -w="/rootfs/$PWD" \ 
    docker/compose:1.13.0'```
  3. run docker-compose with the docker-compose.yml file provided in the myflixKafka repo
    a. `docker-compose up -d`

TO launch the MongoDB instance:
  1. spin up a gcloud instance (coreos)
  2. create MongoDB docker container
    a. ```docker run -d -p 8080:8080 -e MONGO_INITDB_ROOT_USERNAME='restheart' \
    -e MONGO_INITDB_ROOT_PASSWORD='R3ste4rt!'  \
    --name mongodb -v "$PWD/data:/data/db" \
    -v "$PWD/import:/home" mongo:3.6 \
    --bind_ip_all --auth```
  3. migrate videos you want to store to MongoDB instance (either through Github or gcloud scp command):
    a. `gcloud compute scp [LOCAL_FILE_PATH] [INSTANCE_NAME]:~/`
  4. transfer video file to MongoDB container:
    a. `docker cp [FILENAME] [CONTAINER_ID]:/[NAME_GIVEN_TOFILE]`
  5. insert video file into MongoDB/GridFS storage
    a. `docker exec -it [CONTAINER_NAME] mongofiles -d '[DB_NAME]' put [FILE_NAME]`
    
TO launch the MongoDB-2 instance:
  1. Repeat steps for MongoDB instance and upload a different set of videos
  
TO launch the PostgreSQL instance:
  1. spin up a gcloud instance (coreos)
  2. create PostgreSQL docker container
    a. `docker run -d -p 5432:5432 --name postgres postgres`
  3. create the authentication and credit tables in psql
    a. `docker exec -it postgres psql -U postgres`
    b. in psql command line run commands:
      1. `CREATE TABLE authentication(username varchar(50), password varchar(50));`
      2. `CREATE TABLE credit(username varchar(50), card_name varchar(50), \
      card_number bigint, expiry_month integer, expiry_year integer, card_cvv integer);`
      
TO launch the Jenkins instance:
  1. spin up a gcloud instance (coreos)
  2. create Jenkins docker container
    a. `docker run -d -p 50000:50000 -p 8080:8080 --name jenkins jenkins `
  3. follow steps to create a gcloud image and set up github webhook and build steps
    a. https://cloud.google.com/solutions/using-jenkins-for-distributed-builds-on-compute-engine
    
TO launch the Ubuntu/python instance:
  1. jenkins should now take care of spinning up the gcloud instance
  2. insert these commands in the Build - Execute shell window in Jenkins console
    a. ```sudo rm -rf myflixKafka
        git clone https://github.com/adeli321/myflixKafka
        sudo apt-get update
        sudo apt-get install -y \
            apt-transport-https \
            ca-certificates \
            curl \
            gnupg-agent \
            software-properties-common
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
        sudo add-apt-repository \
           "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
           $(lsb_release -cs) \
           stable"
        sudo apt-get update
        sudo apt-get install -y docker-ce docker-ce-cli containerd.io
        ./Buildfile```
        
Now all of the services should be set up.
The only thing left to do is open up the IPs and ports on gcloud.
Necessary ports to open: 8080, 5432, 27017, 2181, 9092
 
