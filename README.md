# mtm2018-cloud-mt-lab
Scalable MT in the Cloud with Marian

# Setup
- Start an Ubuntu 16.04 instance on AWS
- Install Docker
   ```
   curl -fsSL get.docker.com | sh
   ```
- Install Docker Compose
  ```
  curl -L https://github.com/docker/compose/releases/download/1.19.0/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
  chmod +x /usr/local/bin/docker-compose
  ```
- Download data
  ```
  wget http://data.statmt.org/germann/mtm18/mtm18-data.tgz
  ```
- Clone Repo:
  ```
  git clone https://github.com/ugermann/mtm2018-cloud-mt-lab
  ```

- Unpack Data
  ```
  tar xvzf mtm18-data.tgz
  ```
  
- Move everything from mtm18 to docker/marian
  ```
  mv mtm18/* docker/marian
  rmdir mtm18
  ```
  
- Build the Marian Docker image:
  ```
  docker build -t marian docker/marian
  ```
  
- Fire everyhing up with docker-compose
  ```
  cd docker
  docker-compose up
  ```
  
  
