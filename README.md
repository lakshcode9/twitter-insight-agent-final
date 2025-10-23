# Twitter Insight Agent

A command-line application that analyzes Twitter accounts by fetching the last 5 tweets and generating 3 actionable insights using AI.

## Features

- 🔍 **Twitter Analysis**: Fetches the last 5 tweets from any public Twitter account
- 🤖 **AI-Powered Insights**: Uses OpenRouter's NVIDIA Nemotron model to generate actionable insights
- 📊 **Smart Handling**: Gracefully handles edge cases like private accounts, rate limits, and fewer tweets
- 🎯 **Focused Analysis**: Generates exactly 3 concise insights focusing on sentiment, topics, trends, and patterns
- ⚡ **Rate Limit Management**: Built-in retry logic with exponential backoff for reliable operation
- 🔄 **Error Recovery**: Automatic retries and helpful error messages for better user experience

## Installation

### Prerequisites

- Python 3.8 or later
- Twitter API Bearer Token
- OpenRouter API Key

### Setup

1. **Clone or download this repository**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API credentials**:
   
   Create a `.env` file in the project directory with your API credentials:
   ```
   TWITTER_BEARER_TOKEN=your_twitter_bearer_token_here
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   OPENROUTER_MODEL=deepseek/deepseek-r1-distill-qwen-7b
   ```

   **Note**: The `.env` file is already configured with the provided credentials.

## Usage

### Basic Usage

Run the application:
```bash
python twitter_insight_agent.py
```

Enter a Twitter username when prompted:
```
Enter Twitter username (with or without @): elonmusk
```

### Example Output

```
🔍 Analyzing @elonmusk...
📊 Analyzing last 5 tweets
🤖 Generating insights...

📈 Insights for @elonmusk:
==================================================
1. **High Engagement on Innovation Topics**: Recent tweets about AI and space technology are generating significantly more interactions, indicating strong audience interest in cutting-edge technology discussions.

2. **Consistent Posting Pattern**: Maintains regular posting schedule during peak hours (EST), suggesting strategic approach to maximizing reach and engagement with global audience.

3. **Interactive Communication Style**: Notable increase in direct replies to followers, fostering community engagement and personal connection that drives higher retention rates.
==================================================
```

### Commands

- **Enter username**: Type any Twitter username (with or without @)
- **Exit**: Type `quit`, `exit`, or `q` to stop the application
- **Interrupt**: Press `Ctrl+C` to exit at any time

## API Credentials Setup

### Twitter API

1. Go to [Twitter Developer Portal](https://developer.twitter.com/)
2. Create a new app or use existing app
3. Generate a Bearer Token
4. Add the token to your `.env` file

### OpenRouter API

1. Sign up at [OpenRouter](https://openrouter.ai/)
2. Get your API key from the dashboard
3. Add the key to your `.env` file

## Error Handling

The application handles various edge cases:

- **User not found**: Displays error message and asks for another username
- **Private accounts**: Informs user that tweets are not accessible
- **Rate limits**: Shows friendly message suggesting to wait and retry
- **Fewer than 5 tweets**: Analyzes available tweets and notes the limitation
- **Network errors**: Provides clear error messages with suggestions

## Troubleshooting

### Common Issues

1. **"Missing required API credentials"**
   - Ensure your `.env` file exists and contains valid API keys
   - Check that the file is in the same directory as the script

2. **"Twitter API authentication failed"**
   - Verify your Bearer Token is correct and active
   - Check if your Twitter API app has the necessary permissions

3. **"Rate limit exceeded"**
   - The application will automatically retry with exponential backoff
   - Wait for the suggested time before trying again
   - Consider trying different usernames to spread out requests

4. **"Error connecting to AI service"**
   - The application will automatically retry failed requests
   - Check your internet connection
   - Verify your OpenRouter API key is valid

5. **"User not found"**
   - Double-check the username spelling
   - Ensure the account exists and is public
   - Try without the @ symbol

### Rate Limits

- **Twitter API**: Free tier has rate limits (15 requests per 15 minutes for user lookup)
- **OpenRouter**: Free tier available with NVIDIA Nemotron model
- **Automatic Handling**: The application includes built-in retry logic and rate limit management

## Technical Details

- **Twitter API**: Uses Twitter API v2 with Tweepy library
- **AI Model**: NVIDIA Nemotron Nano 9B v2 via OpenRouter (free tier)
- **Tweet Limit**: Fetches up to 5 most recent tweets
- **Response Format**: Always generates exactly 3 numbered insights

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the application.

## License

This project is open source and available under the MIT License.
