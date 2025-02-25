# MCP Client

A client for interacting with Model Context Protocol (MCP) servers.

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure AWS credentials:
   - Copy `.env.sample` to `.env`
   - Edit `.env` to add your AWS credentials:
     ```
     AWS_PROFILE=default
     AWS_REGION=us-east-1
     AWS_ACCESS_KEY_ID=your_access_key_here
     AWS_SECRET_ACCESS_KEY=your_secret_key_here
     ```

## Running the Client

### Using the run_client.sh script (recommended)

The easiest way to run the client is using the provided script:

```bash
./run_client.sh ../../server/weather/weather.py
```

This script will:
1. Check if your `.env` file exists
2. Test your AWS credentials
3. Offer to run with mock responses if credentials fail
4. Start the client with the specified server

### Manual execution

You can also run the client manually:

```bash
source .venv/bin/activate
python client.py ../../server/weather/weather.py
```

## Troubleshooting

### AWS Credential Issues

If you encounter AWS credential errors like:

```
Error invoking Bedrock via litellm: litellm.APIConnectionError: 'NoneType' object has no attribute 'split'
```

This is typically caused by missing or invalid AWS credentials. You can:

1. Run the test script to verify your credentials:
   ```bash
   python test_aws_credentials.py
   ```

2. Use mock responses instead of real API calls:
   ```bash
   export USE_MOCK_RESPONSE=true
   python client.py ../../server/weather/weather.py
   ```

### Common Issues

1. **Missing .env file**: Make sure you've created a `.env` file with your AWS credentials.

2. **Invalid AWS credentials**: Ensure your AWS credentials are correct and have the necessary permissions for Bedrock.

3. **Bedrock access**: Verify your AWS account has access to the Bedrock service and the model you're trying to use.

4. **Region issues**: Make sure you're using a region where Bedrock is available.

## Using Mock Mode

If you don't have AWS Bedrock access or want to test without making real API calls:

```bash
export USE_MOCK_RESPONSE=true
python client.py ../../server/weather/weather.py
```

In mock mode, the client will simulate responses for basic weather queries.