# OpenBB Platform API Keys Guide

## Configuration File Location
Edit `~/.openbb_platform/user_settings.json` with your API keys:

```json
{
  "credentials": {
    "fmp_api_key": "YOUR_FMP_KEY",
    "polygon_api_key": "YOUR_POLYGON_KEY",
    "benzinga_api_key": "YOUR_BENZINGA_KEY", 
    "fred_api_key": "YOUR_FRED_KEY",
    "alpha_vantage_api_key": "YOUR_ALPHA_VANTAGE_KEY",
    "intrinio_api_key": "YOUR_INTRINIO_KEY"
  }
}
```

## How to Get API Keys

### Free Options

#### FRED (Federal Reserve Economic Data)
- **Website**: https://fred.stlouisfed.org/docs/api/api_key.html
- **Cost**: Completely free
- **Requirements**: Just requires registration

#### Alpha Vantage
- **Website**: https://www.alphavantage.co/support/#api-key
- **Cost**: Free tier available
- **Limits**: 25 requests/day on free tier

### Paid/Freemium Options

#### Financial Modeling Prep (FMP)
- **Website**: https://financialmodelingprep.com/developer/docs
- **Cost**: Free tier with limited requests, paid plans available

#### Polygon
- **Website**: https://polygon.io
- **Cost**: Free tier available with rate limits, paid plans for higher usage

#### Benzinga
- **Website**: https://www.benzinga.com/apis
- **Cost**: Primarily paid service

#### Intrinio
- **Website**: https://intrinio.com
- **Cost**: Mostly enterprise/paid plans

## Getting Started Tips

1. **Start with free APIs**: Begin with FRED and Alpha Vantage to test your setup
2. **Check free tiers**: For paid services, explore their free tiers before committing to paid plans
3. **Read the documentation**: Review rate limits and terms of service for each provider
4. **Verify requirements**: Some providers require email verification or additional information
5. **Add gradually**: You don't need all API keys at once - add them as needed

## Setup Process

1. Register for the APIs you need
2. Obtain your API keys from each provider
3. Replace the placeholder text in your `user_settings.json` file with actual API keys
4. Test your configuration with a simple API call

## Notes

- Not all API keys are required to use OpenBB Platform
- You can add keys incrementally as you need access to specific data sources
- Keep your API keys secure and never share them publicly
- Some APIs have usage limits that reset daily/monthly