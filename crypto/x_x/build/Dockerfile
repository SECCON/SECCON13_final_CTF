FROM sagemath/sagemath:10.5

USER root
COPY server.sage .
ENV flag="SECCON{x_x=x.x=x~x=xxx=x_x}"
RUN sage --pip install pycryptodome
RUN apt-get update && apt-get install socat -y
CMD ["sage", "solver.sage"]
CMD ["socat", "TCP-L:31180,fork,reuseaddr", "EXEC:'sage server.sage'"]