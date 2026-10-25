.PHONY: all pipeline site test verify clean reproduce

all: pipeline site test verify

pipeline:
	PYTHONPATH=src python -m mrna_evidence.pipeline

site:
	python scripts/build_site_data.py
	python scripts/build_site_mirror.py

test:
	pytest

verify:
	python scripts/verify.py

reproduce:
	docker compose run --rm lab make all

clean:
	rm -f data/processed/*.csv results/tables/*.csv results/figures/*.png paper/figures/*.png assets/site-data.js
