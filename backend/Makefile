check-venv:
	@if [ -z "$$VIRTUAL_ENV" ]; then \
        echo "Virtual environment is not active. Activate it before running this Make target."; \
        exit 1; \
    fi

server: check-venv
	cd server && python __main__.py


database: check-venv
	cd util/database && python database.py