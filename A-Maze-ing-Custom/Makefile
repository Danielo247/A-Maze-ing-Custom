NAME = a_maze_ing.py
PYTHON = python3
FLAKE8 = python3 -m flake8 .
MYPY = python3 -m mypy

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install flake8 mypy PyQt6


run:
	$(PYTHON) $(NAME) config.txt


debug:
	$(PYTHON) -m pdb $(NAME) config.txt


lint:
	$(FLAKE8)
	$(MYPY) . --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs \
		--check-untyped-defs


lint-strict:
	$(FLAKE8)
	$(MYPY) --strict .


clean:
	rm -rf __pycache__
	rm -rf mazegen/__pycache__
	rm -rf viewer/__pycache__
	rm -rf .mypy_cache
	rm -rf maze.txt

rules:
	$(FLAKE8) .
	$(MYPY) --strict .

.PHONY: install run debug lint lint-strict clean rules
