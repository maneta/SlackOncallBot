FROM centos/python-36-centos7

WORKDIR /opt/app-root/src 

COPY requirements.txt ./  

RUN pip install --no-cache-dir -r requirements.txt

COPY on-call-bot.py ./  

EXPOSE 8080

USER 1001

CMD [ "python", "./on-call-bot.py" ]
