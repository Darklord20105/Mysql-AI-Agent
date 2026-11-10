Ubuntu
│
├── MySQL Server
│   └── Existing database (port 3306)
│
└── Docker
    └── mysql-ai-agent
        └── Python application


mysql read only access user and pass
'ai_agent'@'127.0.0.1'
4d5cb8bc44c8171c6d181750d92cf427547b81660c563520


The supported formats are:
Format	Configuration	File
Excel	xlsx	.xlsx
Word	docx	.docx
PDF	pdf	.pdf
JSON	json	.json
CSV	csv	.csv
Text	txt	.txt

each time you do a change do this to rebuild
sudo docker compose build
sudo docker compose run --rm mysql-ai-agent

to start the container in background
sudo docker compose up -d

to stop it temporarily without removing the container:
sudo docker compose stop

to stop and remove the container
sudo docker compose down

when the container is started we can check the logs by
sudo docker compose logs -f mysql-ai-agent

Check whether the container is running:
sudo docker compose ps