import os
import warnings
import logging

os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

warnings.filterwarnings("ignore")

from transformers.utils import logging as transformers_logging

transformers_logging.set_verbosity_error()

logging.getLogger(
    "huggingface_hub"
).setLevel(
    logging.ERROR
)

from sentence_transformers import SentenceTransformer

_model = None

_embedding_cache = {}


def get_model():

    global _model

    if _model is None:

        _model = SentenceTransformer(
            "BAAI/bge-small-en-v1.5"
        )

    return _model


def embed(text):

    global _embedding_cache

    text = text.strip()

    if text in _embedding_cache:

        return _embedding_cache[text]

    model = get_model()

    embedding = model.encode(

        text,

        normalize_embeddings=True

    ).tolist()

    _embedding_cache[text] = embedding

    return embedding