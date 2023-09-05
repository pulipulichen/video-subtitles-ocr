FROM python:3.9.18-slim-bullseye

RUN pip install --upgrade pip
RUN pip install python-opencv
RUN pip install pytesseract
RUN pip install scikit-image
#RUN scoop install tesseract
RUN apt install tesseract-ocr -y

CMD ["python", "/video-subtitles-ocr.py"]