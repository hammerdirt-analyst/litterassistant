FROM python:3.1

# port
EXPOSE 8080

# upgrade pip and run requirements.txt
COPY requirements.txt equirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# copy the app
COPY litterassistant litterassistant
COPY app.py app.py
WORKDIR .

# run the app
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]