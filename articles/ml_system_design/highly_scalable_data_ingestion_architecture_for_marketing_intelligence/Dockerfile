FROM  public.ecr.aws/lambda/python:3.11 as build

RUN yum install -y unzip && \
    curl -Lo "/tmp/chromedriver-linux64.zip" "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/119.0.6045.105/linux64/chromedriver-linux64.zip" && \
    curl -Lo "/tmp/chrome-linux64.zip" "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/119.0.6045.105/linux64/chrome-linux64.zip" && \
    unzip /tmp/chromedriver-linux64.zip -d /opt/ && \
    unzip /tmp/chrome-linux64.zip -d /opt/


FROM  public.ecr.aws/lambda/python:3.11

# Install the function's OS dependencies using yum
RUN yum install -y \
    atk \
    cups-libs \
    gtk3 \
    libXcomposite \
    alsa-lib \
    libXcursor \
    libXdamage \
    libXext \
    libXi \
    libXrandr \
    libXScrnSaver \
    libXtst \
    pango \
    at-spi2-atk \
    libXt \
    xorg-x11-server-Xvfb \
    xorg-x11-xauth \
    dbus-glib \
    dbus-glib-devel \
    nss \
    mesa-libgbm \
    ffmpeg \
    libxext6 \
    libssl-dev \
    libcurl4-openssl-dev \
    libpq-dev

COPY --from=build /opt/chrome-linux64 /opt/chrome
COPY --from=build /opt/chromedriver-linux64 /opt/

COPY ./pyproject.toml ./poetry.lock ./

RUN python3 -m pip install --upgrade pip && pip install poetry
RUN poetry export -f requirements.txt > requirements.txt && \
    pip3 install  --no-cache-dir -r requirements.txt --target "${LAMBDA_TASK_ROOT}" && \
    rm requirements.txt pyproject.toml poetry.lock

# Copy function code
COPY ./src ${LAMBDA_TASK_ROOT}/src
