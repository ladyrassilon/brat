"""Conversion services, we may want to move these out later on.

Author:     Pontus Stenetorp    <pontus stenetorp>
Version:    2012-06-26
"""



from os.path import join as path_join
from shutil import rmtree
from tempfile import mkdtemp

from ..annotation import Annotations, open_textfile
from ..common import ProtocolError
from ..document import _document_json_dict

from .stanford import basic_dep as stanford_basic_dep
from .stanford import collapsed_ccproc_dep as stanford_collapsed_ccproc_dep
from .stanford import collapsed_dep as stanford_collapsed_dep
from .stanford import coref as stanford_coref
from .stanford import ner as stanford_ner
from .stanford import pos as stanford_pos
from .stanford import sentence_offsets as stanford_sentence_offsets
from .stanford import text as stanford_text
from .stanford import token_offsets as stanford_token_offsets

# Constants
CONV_BY_SRC = {
    'stanford-pos': (stanford_text, stanford_pos, ),
    'stanford-ner': (stanford_text, stanford_ner, ),
    'stanford-coref': (stanford_text, stanford_coref, ),
    'stanford-basic_dep': (stanford_text, stanford_basic_dep, ),
    'stanford-collapsed_dep': (stanford_text, stanford_collapsed_dep, ),
    'stanford-collapsed_ccproc_dep': (stanford_text, stanford_collapsed_ccproc_dep, ),
}
###


class InvalidSrcFormat(ProtocolError):
    def json(self, json_dic):
        json_dic['exception'] = 'InvalidSrcFormat'
        return json_dic


def convert(data, src):
    # Fail early if we don't have a converter
    try:
        conv_text, conv_ann = CONV_BY_SRC[src]
    except KeyError:
        raise InvalidSrcFormat

    # Note: Due to a lack of refactoring we need to write to disk to read
    #   annotions, once this is fixed, the below code needs some clean-up
    tmp_dir = None
    try:
        tmp_dir = mkdtemp()
        doc_base = path_join(tmp_dir, 'tmp')
        with open_textfile(doc_base + '.txt', 'w') as txt_file:
            txt_file.write(conv_text(data))
        with open(doc_base + '.ann', 'w'):
            pass

        with Annotations(doc_base) as ann_obj:
            for ann in conv_ann(data):
                ann_obj.add_annotation(ann)

        json_dic = _document_json_dict(doc_base)
        # Note: Blank the comments, they rarely do anything good but whine
        #   about configuration when we use the tool solely for visualisation
        #   purposes
        json_dic['comments'] = []

        # Note: This is an ugly hack... we want to ride along with the
        #   Stanford tokenisation and sentence splits when returning their
        #   output rather than relying on the ones generated by brat.
        if src.startswith('stanford-'):
            json_dic['token_offsets'] = stanford_token_offsets(data)
            json_dic['sentence_offsets'] = stanford_sentence_offsets(data)

        return json_dic
    finally:
        if tmp_dir is not None:
            rmtree(tmp_dir)
