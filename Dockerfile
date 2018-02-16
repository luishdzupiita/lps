FROM django-scrapper-chrome-and-mozilla4

#Add Python app
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /usr/src/app

RUN chmod 755 /usr/src/app/start.sh

# EXPOSE port 8000 to allow communication to/from server
EXPOSE 8000
EXPOSE 8080
EXPOSE 80

# Alternatively CMD /usr/local/bin/shell.sh ; sleep infinity
CMD ["/usr/src/app/start.sh"]
