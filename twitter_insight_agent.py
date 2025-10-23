#!/usr/bin/env python3
"""
Twitter Insight Agent - Command Line Application

Analyzes the last 5 tweets from a Twitter user and generates 3 actionable insights
using Twitter API v2 and OpenRouter's AI model.
"""

import os
import sys
import requests
import tweepy
import time
from dotenv import load_dotenv
from typing import List, Dict, Any

# Load environment variables
load_dotenv()

class TwitterInsightAgent:
    """Main class for Twitter insight analysis."""
    
    def __init__(self):
        """Initialize the agent with API credentials."""
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        self.openrouter_model = os.getenv('OPENROUTER_MODEL', 'deepseek/deepseek-r1-distill-qwen-7b')
        
        if not self.bearer_token or not self.openrouter_api_key:
            raise ValueError("Missing required API credentials. Please check your .env file.")
        
        # Initialize Twitter API client
        self.twitter_client = tweepy.Client(bearer_token=self.bearer_token)
    
    def get_user_tweets(self, username: str) -> Dict[str, Any]:
        """
        Fetch the last 5 tweets from a Twitter user.
        
        Args:
            username: Twitter username (with or without @)
            
        Returns:
            Dict containing tweets data and metadata
        """
        try:
            # Clean username (remove @ if present)
            clean_username = username.lstrip('@')
            
            # Get user information
            user_response = self.twitter_client.get_user(username=clean_username)
            
            if not user_response.data:
                return {
                    'success': False,
                    'error': f"User '@{clean_username}' not found. Please check the username and try again.",
                    'tweets': [],
                    'user_info': None
                }
            
            user_info = user_response.data
            
            # Check if account is protected
            if hasattr(user_info, 'protected') and user_info.protected:
                return {
                    'success': False,
                    'error': f"Account '@{clean_username}' is private/protected. Cannot access tweets.",
                    'tweets': [],
                    'user_info': user_info
                }
            
            # Get user's tweets
            tweets_response = self.twitter_client.get_users_tweets(
                id=user_info.id,
                max_results=5,
                tweet_fields=['created_at', 'public_metrics']
            )
            
            tweets = []
            if tweets_response.data:
                tweets = [tweet.text for tweet in tweets_response.data]
            
            return {
                'success': True,
                'tweets': tweets,
                'user_info': user_info,
                'tweet_count': len(tweets)
            }
            
        except tweepy.TooManyRequests as e:
            # Extract rate limit reset time if available
            reset_time = None
            if hasattr(e, 'response') and e.response is not None:
                reset_time = e.response.headers.get('x-rate-limit-reset')
                if reset_time:
                    reset_time = int(reset_time)
            
            error_msg = "Twitter API rate limit exceeded. Please wait 15 minutes and try again."
            if reset_time:
                current_time = int(time.time())
                wait_time = reset_time - current_time
                if wait_time > 0:
                    error_msg = f"Twitter API rate limit exceeded. Please wait {wait_time} seconds and try again."
            
            return {
                'success': False,
                'error': error_msg,
                'tweets': [],
                'user_info': None
            }
        except tweepy.Unauthorized:
            return {
                'success': False,
                'error': "Twitter API authentication failed. The Bearer Token needs to be from a Twitter Developer App attached to a Project. Please check your credentials in the Twitter Developer Portal.",
                'tweets': [],
                'user_info': None
            }
        except tweepy.Forbidden:
            return {
                'success': False,
                'error': "Twitter API access forbidden. The Bearer Token needs to be from a Twitter Developer App attached to a Project. Please check your Twitter Developer Portal settings.",
                'tweets': [],
                'user_info': None
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Error fetching tweets: {str(e)}",
                'tweets': [],
                'user_info': None
            }
    
    def generate_insights(self, tweets: List[str], tweet_count: int) -> str:
        """
        Generate insights using OpenRouter API.
        
        Args:
            tweets: List of tweet texts
            tweet_count: Number of tweets available
            
        Returns:
            Generated insights as formatted string
        """
        if not tweets:
            return "No tweets available for analysis."
        
        # Prepare tweets text
        tweets_text = "\n".join([f"Tweet {i+1}: {tweet}" for i, tweet in enumerate(tweets)])
        
        # Construct prompt
        prompt = f"""Analyze the following {tweet_count} tweets and generate exactly 3 concise, actionable insights. Focus on sentiment, main topics, trends, or notable patterns. Each insight must be unique and specific to the content provided. Format your response as a numbered list (1-3).

Tweets to analyze:
{tweets_text}

Requirements:
- Each insight should be 1-2 sentences
- Focus on actionable observations
- Avoid vague statements
- Be specific to the tweet content
- Number each insight (1, 2, 3)"""
        
        # Retry logic with exponential backoff
        max_retries = 3
        base_delay = 1
        
        for attempt in range(max_retries):
            try:
                headers = {
                    'Authorization': f'Bearer {self.openrouter_api_key}',
                    'Content-Type': 'application/json',
                    'HTTP-Referer': 'https://github.com/twitter-insight-agent',
                    'X-Title': 'Twitter Insight Agent'
                }
                
                data = {
                    'model': self.openrouter_model,
                    'prompt': prompt,
                    'max_tokens': 300,
                    'temperature': 0.7
                }
                
                response = requests.post(
                    'https://openrouter.ai/api/v1/completions',
                    headers=headers,
                    json=data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    insights = result['choices'][0]['text'].strip()
                    return insights
                elif response.status_code == 429:
                    # Rate limited - wait and retry
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        print(f"⚠️  Rate limited. Waiting {delay} seconds before retry...")
                        time.sleep(delay)
                        continue
                    else:
                        return "AI service is currently busy. Please try again in a few minutes."
                else:
                    return f"Error generating insights: {response.status_code} - {response.text}"
                    
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    print(f"⚠️  Request timed out. Retrying in {delay} seconds...")
                    time.sleep(delay)
                    continue
                else:
                    return "Request timed out. Please try again."
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    print(f"⚠️  Connection error. Retrying in {delay} seconds...")
                    time.sleep(delay)
                    continue
                else:
                    return f"Error connecting to AI service: {str(e)}"
            except Exception as e:
                return f"Error generating insights: {str(e)}"
        
        return "Failed to generate insights after multiple attempts. Please try again later."
    
    def analyze_user(self, username: str) -> None:
        """
        Analyze a Twitter user and display insights.
        
        Args:
            username: Twitter username to analyze
        """
        print(f"\n🔍 Analyzing @{username.lstrip('@')}...")
        
        # Add a small delay to prevent rate limiting
        time.sleep(1)
        
        # Fetch tweets
        result = self.get_user_tweets(username)
        
        if not result['success']:
            print(f"❌ {result['error']}")
            
            # If it's a rate limit error, suggest waiting
            if "rate limit" in result['error'].lower():
                print("💡 Tip: Wait a few minutes before trying again, or try a different username.")
            
            return
        
        tweets = result['tweets']
        tweet_count = result['tweet_count']
        
        if not tweets:
            print(f"📭 No tweets found for @{username.lstrip('@')}")
            return
        
        # Display tweet count info
        if tweet_count < 5:
            print(f"📊 Found {tweet_count} tweets (less than 5 available)")
        else:
            print("📊 Analyzing last 5 tweets")
        
        # Generate insights
        print("🤖 Generating insights...")
        insights = self.generate_insights(tweets, tweet_count)
        
        # Display results
        print(f"\n📈 Insights for @{username.lstrip('@')}:")
        print("=" * 50)
        print(insights)
        print("=" * 50)
    
    def run(self) -> None:
        """Main CLI loop."""
        print("🐦 Twitter Insight Agent")
        print("=" * 30)
        print("Analyze Twitter accounts and get actionable insights!")
        print("Type 'quit' or 'exit' to stop.\n")
        
        while True:
            try:
                username = input("Enter Twitter username (with or without @): ").strip()
                
                if username.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if not username:
                    print("Please enter a valid username.")
                    continue
                
                self.analyze_user(username)
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {str(e)}")


def main():
    """Main entry point."""
    try:
        agent = TwitterInsightAgent()
        agent.run()
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("Please check your .env file and ensure all required API keys are set.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Fatal Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
