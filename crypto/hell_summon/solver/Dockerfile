FROM sagemath/sagemath:10.5

USER root
# COPY rkm.sage .
RUN apt-get update && apt-get -y install curl
RUN curl https://raw.githubusercontent.com/maple3142/lll_cvp/refs/heads/master/lll_cvp.py > lll_cvp.py
RUN sage --pip install pycryptodome pwntools tqdm logger

COPY ./y011d4_solver.sage .
CMD ["sage", "y011d4_solver.sage"]
