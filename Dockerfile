FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11

WORKDIR /app/

# Install Poetry
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    apt update && apt install -y golang tmux

# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./pyproject.toml ./poetry.lock* /app/

# Allow installing dev dependencies to run tests
ARG INSTALL_DEV=false
RUN bash -c "if [ $INSTALL_DEV == 'true' ] ; then poetry install --no-root ; else poetry install --no-root --no-dev ; fi"

COPY . /app
ENV PYTHONPATH=/app PATH=/root/go/bin:$PATH

RUN GO111MODULE=on go install github.com/DarthSim/overmind/v2@latest

CMD ["overmind", "start"]

