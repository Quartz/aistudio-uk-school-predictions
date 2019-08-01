import numpy as np
from fastai.text import *
from fastprogress import force_console_behavior
master_bar, progress_bar = force_console_behavior()

"""
Create a language model and encoder with fastai. A language model is a
probability distribution over sequences of words that tries to distinguish
between words and phrases that sound similar.
"""

np.random.seed(42)
data_lm = TextLMDataBunch.from_csv(path='./', 'school_sample.csv', text_cols='text', label_cols='label')
print ("loading data model...")
# data_lm.show_batch()
# List unique possible tokens
print (data_lm.vocab.itos[:20])
print (len(data_lm.vocab.itos))
data_lm.save('data_lm.pkl')
data_lm = load_data('./', 'data_lm.pkl', bs=60)

# Make a language model encoder
learn = language_model_learner(data_lm, AWD_LSTM, drop_mult=0.3).to_fp16()
learn.lr_find()
# learn.recorder.plot()
print ("fitting one cycle")
learn.fit_one_cycle(1, 2e-2, moms=(0.8,0.7))
learn.save('bs60-awdlstm-stage1')
learn.load('bs60-awdlstm-stage1')
learn.unfreeze()
learn.lr_find()
# learn.recorder.plot(skip_end=5)
learn.save('bs60-awdlstm-stage2')
learn.load('bs60-awdlstm-stage2')
learn.unfreeze()
learn.lr_find()
# learn.recorder.plot(skip_end=5)
learn.unfreeze()
learn.fit_one_cycle(1, 1e-4, moms=(0.8,0.7))
learn.save('bs60-awdlstm-stage2-2')
learn.save_encoder('bs60-awdlstm-enc-stage2')

with open('lm_test.txt','w') as f:
	TEXT = "This school is"
	N_WORDS = 40
	for temp in [0.1,0.5,1,1.5,2,2.5]:
		f.write(learn.predict(TEXT, N_WORDS, temperature=temp))
		f.write('\n')
		f.write('-'*10)
