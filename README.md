
## Installation

1. Clone the repository and navigate to the project directory:

```bash
git clone https://github.com/volchey/Bringg.git
cd Bringg
```

2. Build the Docker image:

```bash
docker build -t fedex-tracker .
```

3. Run a container:

```bash
docker run -p 8000:8000 fedex-tracker
```