# Use an official Python runtime as a parent image
FROM python:3.10-slim
WORKDIR /app

COPY . /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

ENV OPENAI_API_KEY=""
# Make port 7860 available to the world outside this container
# (7860 is the default port for Gradio)
EXPOSE 7860


# Run airport_app_openai.py when the container launches
CMD ["python", "airport_app_openai.py"]