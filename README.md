# Stock Price Analysis and Algorithmic Trading

## Preliminaries
- Make sure Docker is installed. If it's not, you can download it from the [here](https://www.docker.com/products/docker-desktop). 
- docker-compose should also be installed
- Make sure you have MySQL downloaded locally, as well as python
- Ensure that project has permissions to access MySQL root (password is currently set to "easy")
- If you are not using an ARM chip, got to docker-compose.yaml and change line 4 to `image: mysql:latest` and line 14 to `image: phpmyadmin/phpmyadmin`
  
## Setup
- On the terminal, navigate the project directory and run the command: `docker-compose up -d`
- install the requirements via `pip3 install -r requirements.txt`
  
## Execution
- Run `python <file_name>`
- Access the Database UI at the url `http://localhost:8080/phpmyadmin`
