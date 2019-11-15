# Beta tensorflow... RIP
FROM tensorflow/tensorflow:0.12.1-gpu-py3

# Fix for CV2
RUN apt-get update && \
    apt-get install -y libsm6 libxext6 libxrender-dev

# Dataset and results paths.
ENV datasets /datasets
ENV results /results

# Declare the volumes
VOLUME ${datasets} ${results}

# Make the directories in root.
RUN mkdir /src

# Copy requiremenets file to the src dir.
WORKDIR /src
COPY requirements.txt /src

# Install pip modules
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the code.
COPY . /src