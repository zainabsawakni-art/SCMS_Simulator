# Flask Web Application

A basic Flask web application with essential structure.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open your browser and navigate to:
```
http://localhost:5000
```

## Project Structure

```
.
├── app.py              # Main application file
├── config.py           # Configuration settings
├── requirements.txt    # Python dependencies
├── templates/          # HTML templates
│   └── index.html
└── README.md           # This file
```

## Environment Variables

You can configure the application using environment variables:

- `SECRET_KEY`: Secret key for Flask sessions (default: dev key)
- `FLASK_DEBUG`: Enable debug mode (default: False)
- `FLASK_HOST`: Host to bind to (default: 0.0.0.0)
- `FLASK_PORT`: Port to bind to (default: 5000)
