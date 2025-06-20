from setuptools import setup, find_packages

setup(
    name="audionexus",
    version="0.3.3",
    packages=find_packages(where="app"),
    package_dir={"": "app"},
    install_requires=[
        # Core
        "fastapi>=0.95.0",
        "uvicorn[standard]>=0.21.1",
        "python-dotenv>=1.0.0",
        "python-multipart>=0.0.6",
        
        # Database
        "sqlalchemy>=2.0.0",
        "alembic>=1.11.0",
        "psycopg2-binary>=2.9.5",
        
        # Authentication & Security
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
        "python-magic>=0.4.27",
        "email-validator>=2.0.0",
        
        # API & HTTP
        "httpx>=0.24.0",
        "pydantic>=1.10.7",
        "aiohttp>=3.8.4",
        "python-socketio>=5.8.0",
        
        # Audio Processing
        "mutagen>=1.46.0",
        "pydub>=0.25.1",
        
        # Utilities
        "aiofiles>=23.1.0",
        "python-slugify>=7.0.0",
    ],
    extras_require={
        "test": [
            "pytest>=7.3.1",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "pytest-httpx>=0.23.3",
            "factory-boy>=3.2.1",
            "faker>=18.13.0",
            "responses>=0.23.1",
        ]
    },
    python_requires=">=3.8",
)
