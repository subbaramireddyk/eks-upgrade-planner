# Multi-stage build for EKS Upgrade Planner
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install AWS CLI
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install \
    && rm -rf awscliv2.zip aws

# Install kubectl
RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" \
    && install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl \
    && rm kubectl

# Create non-root user
RUN useradd -m -u 1000 -s /bin/bash eksplanner

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /home/eksplanner/.local

# Copy application code
COPY src/ ./src/
COPY data/ ./data/
COPY config/ ./config/
COPY setup.py .
COPY requirements.txt .
COPY README.md .

# Set ownership
RUN chown -R eksplanner:eksplanner /app

# Switch to non-root user
USER eksplanner

# Add local bin to PATH
ENV PATH=/home/eksplanner/.local/bin:$PATH

# Install package
RUN pip install --no-cache-dir --user -e .

ENTRYPOINT ["eks-upgrade-planner"]
CMD ["--help"]
