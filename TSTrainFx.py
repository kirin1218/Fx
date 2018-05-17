#-*- coding:utf-8 -*-
#from tensorflow.examples.tutorials.mnist import input_data
#import tensorflow as tf
import Fx

#入力データ整形
num_seq = 4
num_input = 60
num_weight = 32
num_result = 3

#mnistデータを格納したオブジェクトを呼び出す
#mnist = input_data.read_data_sets("data/", one_hot=True)
fxDS = Fx.read_data_sets(train_size=240,test_size=100,one_hot=True)
fxDS.train_datas.print()
'''
print(fxDS.train.labels)
"""モデル構築開始"""
x = tf.placeholder(tf.float32, [None, num_seq*num_input])
#(バッチサイズ,高さ, 幅)の2階テンソルに変換
input = tf.reshape(x, [-1, num_seq, num_input])

#ユニット数128個のLSTMセル
#三段に積む
stacked_cells = []
stacked_cells.append(tf.nn.rnn_cell.LSTMCell(num_units=num_weight))
stacked_cells.append(tf.nn.rnn_cell.LSTMCell(num_units=num_weight))
stacked_cells.append(tf.nn.rnn_cell.LSTMCell(num_units=num_weight))

cell = tf.nn.rnn_cell.MultiRNNCell(cells=stacked_cells)

outputs, states = tf.nn.dynamic_rnn(cell=cell, inputs=input, dtype=tf.float32)

#3階テンソルを2階テンソルのリストに変換
outputs_list = tf.unstack(outputs, axis=1)
#最終時系列情報を取得
last_output = outputs_list[-1]

w = tf.Variable(tf.truncated_normal([num_weight,num_result], stddev=0.1))
b = tf.Variable(tf.zeros([num_result]))

out = tf.nn.softmax(tf.matmul(last_output, w ) + b)

#正解データの型を定義
y = tf.placeholder(tf.float32, [None, num_result])
#誤差関数（クロスエントロピー）
loss = tf.reduce_mean(-tf.reduce_sum(y * tf.log(out), axis=[1]))

#訓練
train_step = tf.train.GradientDescentOptimizer(0.1).minimize(loss)

#評価
correct = tf.equal(tf.argmax(out,1), tf.argmax(y,1))
accuracy = tf.reduce_mean(tf.cast(correct, tf.float32))

init = tf.global_variables_initializer()

with tf.Session() as sess:
    sess.run(init)
    #テストデータをロード
    test_datas = fxDS.test.datas
    test_labels = fxDS.test.labels

    for i in range(1000):
        step = i+1
        train_datas, train_labels = fxDS.train.next_batch(50)
        sess.run(train_step, feed_dict={x:train_datas ,y:train_labels})

        #10階ごとに精度を検証
        if step % 100 == 0:
            acc_val = sess.run( accuracy, feed_dict={x:test_datas, y:test_labels})
            print('Step %d: accuracy = %.2f' % (step, acc_val))
'''