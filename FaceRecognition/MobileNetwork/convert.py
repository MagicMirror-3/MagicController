import tensorflow as tf

resnet_v2_101 = tf.keras.Sequential([
  tf.keras.layers.InputLayer(input_shape=(112, 112, 3)),
  hub.KerasLayer("https://tfhub.dev/google/imagenet/resnet_v2_101/classification/4")
])

converter = tf.lite.TFLiteConverter.from_keras_model(resnet_v2_101)


# Convert to TF Lite without quantization
resnet_tflite_file = tflite_models_dir/"resnet_v2_101.tflite"
resnet_tflite_file.write_bytes(converter.convert())

# -------------------------------------------------------------------------------

# Convert to TF Lite with quantization
converter.optimizations = [tf.lite.Optimize.DEFAULT]
resnet_quantized_tflite_file = tflite_models_dir/"resnet_v2_101_quantized.tflite"
resnet_quantized_tflite_file.write_bytes(converter.convert())

