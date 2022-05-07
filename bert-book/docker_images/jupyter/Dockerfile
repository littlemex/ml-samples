FROM huggingface/transformers-pytorch-gpu:4.18.0

USER root

RUN pip install --no-cache-dir \
  lightgbm==3.2.1 \
  transformers==4.5.0 \
  fugashi==1.1.0 \
  ipadic==1.0.0 \
  jupyter

RUN mkdir -p /home/root/work

EXPOSE 8080

# docker run -it --rm --gpus all huggingface/transformers-pytorch-gpu:4.18.0 bash
# matplotlibで日本語を使えるようにする
#RUN sed -i '/font\.family/d' /opt/conda/lib/python3.9/site-packages/matplotlib/mpl-data/matplotlibrc
#RUN echo "font.family: IPAexGothic" >> /opt/conda/lib/python3.9/site-packages/matplotlib/mpl-data/matplotlibrc
#RUN rm -rf /home/jovyan/.cache
