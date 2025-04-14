FROM sagemath/sagemath:10.5

USER root
COPY solver.sage .

RUN sage --pip install pycryptodome pwntools tqdm logger
CMD ["sage", "solver.sage"]
