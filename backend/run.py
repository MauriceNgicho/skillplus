from app import create_app

# Expose the Flask application for the `flask` CLI (FLASK_APP=run:app)
app = create_app('development')


if __name__ == '__main__':
	app.run(debug=True)
