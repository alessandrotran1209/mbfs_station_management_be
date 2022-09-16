#
FROM python:3.10

#
WORKDIR /be

#
COPY ./mbfs_station_management_be/requirements.txt /be/requirements.txt

#
RUN pip install --no-cache-dir --upgrade -r /be/requirements.txt

#
COPY ../mbfs_station_management_be /be

EXPOSE 8000

#
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
