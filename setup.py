from setuptools import setup, find_packages


with open("requirements.txt") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.strip().startswith('-e')]

setup(
    name = "doctor-appointment-agentic" ,
    version="0.0.1",
    author="Sayed Ali",
    author_email="saiedhassaan2@gmail.com",
    packages=find_packages(),
    install_requires=requirements,
    python_requires=">=3.10",  # Ensure compatible Python version
)