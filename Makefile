build_bitext:
	cd src;	python make_bitext.py -s ../data/hachidaishu/hachidai.db -t ../data/translations/all_translations.txt -o ../cache/bitexts.csv
build_metacode2lemma_dict:
	cd src;	python make_metacode2lemma.py -f ../data/hachidaishu/hachidai.db -o ../cache/metacode2lemma_src.pkl -t source; python make_metacode2lemma.py -f ../data/translations/all_translations.txt -o ../cache/metacode2lemma_tar.pkl -t target
train_save_ibm2:
	cd src; python train_save_model.py -c ../cache/bitexts.csv -f ibm2_fwd.model -b ibm2_bwd.model -m ibm2
save_db:
	cd src; python bitexts.py -o ../cache/bitexts.db -m ibm2 -t kaneko katagiri kojimaarai komachiya kubota kyusojin matsuda okumura ozawa takeoka
basic_stat:
	cd src; python stat.py; column -s, -t ../artifacts/basic_stat.csv
accuracy:
	cd src; python accuracy.py; column -s, -t ../artifacts/accuracy.csv

WORDS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
$(eval $(WORDS):;@:)
plot_overall:
	cd src; python visualize_aggregate_overall.py -w $(WORDS)
plot_by_translator:
	cd src; python visualize_aggregate_translator.py -w $(WORDS)
plot_indivisual:
	cd src; python visualize_indivisual.py -w $(WORDS)
plot_aligment:
	cd src; python visualize_alignment.py -w $(WORDS) -t kaneko -m source2target  
app:
	cd src; python app.py
