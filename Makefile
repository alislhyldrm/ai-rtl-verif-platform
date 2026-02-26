.PHONY: help smoke test clean

help:
	@echo "Targets:"
	@echo "  make smoke   - run cocotb+verilator smoke test"
	@echo "  make test    - run all tests"
	@echo "  make clean   - remove build/test artifacts"

smoke:
	pytest -q

test:
	pytest -q

clean:
	rm -rf reports/latest/sim_build .pytest_cache tests/__pycache__