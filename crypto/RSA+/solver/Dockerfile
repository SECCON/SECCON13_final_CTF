FROM sagemath/sagemath:10.5

ENV TMPDIR=/tmp

WORKDIR /app

RUN chmod 777 /app

RUN sage -pip install --no-cache pwntools==4.13.1
COPY solve.sage /app/solve.sage

CMD ["sage", "/app/solve.sage"]
