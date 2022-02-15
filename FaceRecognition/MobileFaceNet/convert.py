"""
from:

https://github.com/sirius-ai/MobileFaceNet_TF/tree/master/arch/pretrained_model

loading: https://stackoverflow.com/questions/51278213/what-is-the-use-of-a-pb-file-in-tensorflow-and-how-does-it-work


load frozen graph: https://leimao.github.io/blog/Save-Load-Inference-From-TF2-Frozen-Graph/
"""

import tensorflow as tf


def load_pb(path_to_pb):
    with tf.compat.v1.gfile.GFile(path_to_pb, "rb") as f:
        graph_def = tf.compat.v1.GraphDef()
        graph_def.ParseFromString(f.read())
    with tf.Graph().as_default() as graph:
        tf.import_graph_def(graph_def, name='')
        return graph


graph = load_pb("model/FaceMobileNet192_train_false.pb")

input = graph.get_tensor_by_name('input:0')
output = graph.get_tensor_by_name('output:0')

sess.run(output, feed_dict={input: some_data})
