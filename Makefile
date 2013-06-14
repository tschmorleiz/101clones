run:
	@python program.py fragment 0.1 resultsFragment.json
	@python program.py diff 0.25 resultsDiff.json
	@make clean

clean:
	@rm -f extract1.json
	@rm -f extract2.json
	@rm -f input.py
	@rm -f input1.py
	@rm -f input2.py
	@rm -f result.py
	@rm -f result.json
	@rm -f program.py~

