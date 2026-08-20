FROM mysql:latest

COPY sql-init-script/ /docker-entrypoint-initdb.d/

EXPOSE 3306
EXPOSE 33060

CMD [ "mysqld" ]