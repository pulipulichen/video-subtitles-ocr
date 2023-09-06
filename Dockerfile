FROM breezedeus/cnocr:v2.2

CMD ["python", "/script/main.py"]

RUN pip install moviepy
RUN pip install Pillow
RUN pip install fuzzywuzzy