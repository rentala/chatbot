
import os
import sys
import json
import shutil
import pickle
import logging
import data_helper
import numpy as np
import pandas as pd
import tensorflow as tf
from text_cnn_rnn import TextCNNRNN


logging.getLogger().setLevel(logging.INFO)

def load_trained_params(trained_dir):
	params = json.loads(open(trained_dir + 'trained_parameters.json').read())
	##print (params)
	words_index = json.loads(open(trained_dir + 'words_index.json').read())
	##print (words_index)
	labels = json.loads(open(trained_dir + 'labels.json').read())
	##print (labels)

	with open(trained_dir + 'embeddings.pickle', 'rb') as input_file:
		fetched_embedding = pickle.load(input_file)
	embedding_mat = np.array(fetched_embedding, dtype = np.float32)
	return params, words_index, labels, embedding_mat

def load_test_data(test_file, labels):
	df = pd.read_csv(test_file)
	select = ['Descript']
	##print (df)
	df = df.dropna(axis=0, how='any', subset=select)
	#print (df)
	test_examples = df[select[0]].apply(lambda x: data_helper.clean_str(x).split(' ')).tolist()

	num_labels = len(labels)
	one_hot = np.zeros((num_labels, num_labels), int)
	np.fill_diagonal(one_hot, 1)
	label_dict = dict(zip(labels, one_hot))

	y_ = None
	if 'Category' in df.columns:
		select.append('Category')
		y_ = df[select[1]].apply(lambda x: label_dict[x]).tolist()

	not_select = list(set(df.columns) - set(select))
	df = df.drop(not_select, axis=1)
	return test_examples, y_, df

def map_word_to_index(examples, words_index):
	x_ = []
	for example in examples:
		temp = []
		for word in example:
			if word in words_index:
				temp.append(words_index[word])
			else:
				temp.append(0)
		x_.append(temp)
	return x_
def normalize(v):
    norm=np.linalg.norm(v, ord=1)
    if norm==0:
        norm=np.finfo(v.dtype).eps
    return v/norm

params, words_index, labels, embedding_mat = load_trained_params(trained_dir)

def predict_unseen_data():
	test_x = []
	#test_input = os.environ.get('TEST_X', None)
	test_input = "What time is the class"

	if test_input is None:
		logging.critical(' TEST_X is not found ')
		sys.exit()
	test_x.append(test_input.split(' '))
	trained_dir = "trained_results_1512435063"
	#os.environ.get('TRAINED_RESULTS', None)



	if trained_dir is None:
		logging.critical(' TRAINED_RESULTS is not found ')
		sys.exit()

	if not trained_dir.endswith('/'):
		trained_dir += '/'

	x_ = data_helper.pad_sentences(test_x, forced_sequence_length=params['sequence_length'])
	x_ = map_word_to_index(x_, words_index)

	x_test, y_test = np.asarray(x_), None

	timestamp = trained_dir.split('/')[-2].split('_')[-1]

	with tf.Graph().as_default():
		session_conf = tf.ConfigProto(allow_soft_placement=True, log_device_placement=False)
		sess = tf.Session(config=session_conf)
		with sess.as_default():
			cnn_rnn = TextCNNRNN(
				embedding_mat = embedding_mat,
				non_static = params['non_static'],
				hidden_unit = params['hidden_unit'],
				sequence_length = len(x_test[0]),
				max_pool_size = params['max_pool_size'],
				filter_sizes = map(int, params['filter_sizes'].split(",")),
				num_filters = params['num_filters'],
				num_classes = len(labels),
				embedding_size = params['embedding_dim'],
				l2_reg_lambda = params['l2_reg_lambda'])

			def real_len(batches):
				return [np.ceil(np.argmin(batch + [0]) * 1.0 / params['max_pool_size']) for batch in batches]

			def predict_step(x_batch):
				feed_dict = {
					cnn_rnn.input_x: x_batch,
					cnn_rnn.dropout_keep_prob: 1.0,
					cnn_rnn.batch_size: len(x_batch),
					cnn_rnn.pad: np.zeros([len(x_batch), 1, params['embedding_dim'], 1]),
					cnn_rnn.real_len: real_len(x_batch),
				}
				scores,predictions = sess.run([cnn_rnn.scores,cnn_rnn.predictions], feed_dict)
				return scores,predictions

			checkpoint_file = trained_dir + 'best_model.ckpt'
			saver = tf.train.Saver(tf.all_variables())
			saver = tf.train.import_meta_graph("{}.meta".format(checkpoint_file))
			saver.restore(sess, checkpoint_file)
			logging.critical('{} has been loaded'.format(checkpoint_file))

			batches = data_helper.batch_iter(list(x_test), params['batch_size'], 1, shuffle=False)
			response=""
			predictions, predict_labels = [], []
			for x_batch in batches:
				scores,batch_predictions = predict_step(x_batch)
				print scores
				score=normalize(scores[0])
				print score
				print score.max()
				mscore=score.max()
				range_perc = 0.01

				max_range = mscore + (mscore * range_perc)
				min_range = mscore - (mscore * range_perc)

				for s in score:
					if(s > min_range and s < max_range)


				max_score = score.max()
				if(max_score>0.1):
					print scores
					for batch_prediction in batch_predictions:
						predictions.append(batch_prediction)
						predict_labels.append(labels[batch_prediction])
					response= predict_labels[0]
				else:
					response="Fall back!"
			sys.stdout.write(response)
			print response

			os.environ['PRED_LABEL'] = response


if __name__ == '__main__':
	# python3 predict.py ./trained_results_1478563595/ ./data/small_samples.csv
	predict_unseen_data()
