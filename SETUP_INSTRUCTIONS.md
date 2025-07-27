# OpenBB Platform Local Setup Instructions

This guide provides complete instructions for installing and running OpenBB Platform locally with custom startup scripts.

## Overview

OpenBB is an open-source financial data platform that provides:
- **Core Platform**: Modular architecture for financial data access
- **CLI Interface**: Command-line interface for interactive use
- **REST API**: FastAPI server for programmatic access
- **Extensions**: Domain-specific modules (equity, crypto, economy, etc.)
- **Providers**: 30+ data provider integrations (Alpha Vantage, Bloomberg, FMP, Yahoo Finance, etc.)

## Prerequisites

- **Python 3.9+** - Required for OpenBB Platform
- **Poetry** - For dependency management (auto-installed by script if missing)
- **Conda** (optional) - For isolated environment management

## Installation

### Quick Start

1. **Run the installation script:**
   ```bash
   ./install_openbb.sh
   ```

2. **Choose installation method:**
   - `1` - Development installation (editable, from source)
   - `2` - Production installation (`pip install openbb`)
   - `3` - Production with all extensions (`pip install openbb[all]`)

3. **Add your API keys:**
   Edit `~/.openbb_platform/user_settings.json` with your API keys:
   ```json
   {
     "credentials": {
       "fmp_api_key": "YOUR_FMP_KEY",
       "polygon_api_key": "YOUR_POLYGON_KEY",
       "benzinga_api_key": "YOUR_BENZINGA_KEY", 
       "fred_api_key": "YOUR_FRED_KEY",
       "alpha_vantage_api_key": "YOUR_ALPHA_VANTAGE_KEY",
       "intrinio_api_key": "YOUR_INTRINIO_KEY",
       "quandl_api_key": "YOUR_QUANDL_KEY",
       "twelvedata_api_key": "YOUR_TWELVEDATA_KEY"
     }
   }
   ```

### API Key Recommendations

**Priority Recommendations** - Most Important to Get Next:
1. **Polygon.io** - Great for real-time data and professional-grade endpoints
2. **Twelve Data** - High daily limit (800 calls) for free tier

**Quick Sign-up Links:**
1. **Polygon**: https://polygon.io/dashboard/signup
2. **Twelve Data**: https://twelvedata.com/pricing (Free plan)
3. **Quandl/NASDAQ**: https://data.nasdaq.com/sign-up

**Testing Your Current Setup:**
You can test your API keys work by running this in Jupyter or Python:
```python
from openbb import obb

# Test FMP (stock data)
data = obb.equity.price.historical("AAPL", provider="fmp")
print("FMP:", data.to_dataframe().head())

# Test Alpha Vantage
data = obb.equity.price.historical("AAPL", provider="alpha_vantage")
print("Alpha Vantage:", data.to_dataframe().head())

# Test FRED (economic data)
data = obb.economy.fred.series("GDP")
print("FRED:", data.to_dataframe().head())
```

Your current setup with FMP, FRED, and Alpha Vantage should give you access to most stock data, company fundamentals, and economic indicators. The additional keys will provide more data sources and higher rate limits.

**Important**: After adding or updating API keys, you need to restart OpenBB services to load the new configuration:
```bash
# Stop current services
./stop_all.sh

# Start services with new API keys
./start_all.sh
```

Alternatively, you can set API keys programmatically in Python (temporary for that session):
```python
from openbb import obb

# Set credentials at runtime
obb.user.credentials.polygon_api_key = "your_new_key_here"
obb.user.credentials.twelvedata_api_key = "your_new_key_here"

# Save to config file (optional)
obb.account.save()
```

### Environment Setup (Optional)

The installation script can create a Conda environment using the existing `environment.yml` file:
- Environment name: `alfa-class-env` (configured for this project)
- Includes data science packages (pandas, numpy, matplotlib, etc.)
- Installs as Jupyter kernel for easy notebook access

## Available Scripts

### Individual Service Scripts

| Script | Purpose | Default Location |
|--------|---------|------------------|
| `./start_jupyter.sh` | Start Jupyter Lab | http://localhost:8888 |
| `./start_api.sh` | Start REST API server | http://localhost:8000 |
| `./start_cli.sh` | Start OpenBB CLI | Terminal interface |

### Combined Management Scripts

| Script | Purpose |
|--------|---------|
| `./start_all.sh` | Start Jupyter Lab + API server |
| `./stop_all.sh` | Stop all OpenBB services |

## Usage Instructions

### Starting Services

**Start everything at once:**
```bash
./start_all.sh
```

**Start individual services:**
```bash
# Jupyter Lab (integrates with existing jlab aliases)
./start_jupyter.sh

# REST API server  
./start_api.sh

# Command-line interface
./start_cli.sh
```

### Jupyter Lab Integration

The Jupyter startup script integrates with your existing bash aliases:

**Your existing aliases still work:**
```bash
jps     # Show Jupyter processes
jstop   # Stop Jupyter Lab  
jkill   # Kill all Jupyter processes
```

**Configuration matches your setup:**
- IP: `0.0.0.0` (accessible from any interface)
- Port: `8888`
- Runs in background with logging to `~/jupyter.log`
- Starts in `examples/` directory if available

### REST API Usage

**API Server:**
- Base URL: http://localhost:8000
- Documentation: http://localhost:8000/docs
- Interactive API testing available in docs

**Example API calls:**
```bash
# Get historical price data
curl "http://localhost:8000/api/v1/equity/price/historical?symbol=AAPL"

# Get company profile
curl "http://localhost:8000/api/v1/equity/profile?symbol=AAPL"
```

### Python Usage

**Basic usage:**
```python
from openbb import obb

# Get historical stock data
output = obb.equity.price.historical("AAPL")
df = output.to_dataframe()
print(df.head())

# Get company profile
profile = obb.equity.profile("AAPL")
print(profile)
```

**With API keys configured:**
```python
from openbb import obb

# Set credentials at runtime (alternative to config file)
obb.user.credentials.fmp_api_key = "your_key_here"
obb.user.credentials.polygon_api_key = "your_key_here"

# Save settings
obb.account.save()
```

## Service Management

### Checking Service Status

**View running processes:**
```bash
# Jupyter processes
jps

# All OpenBB processes  
ps aux | grep -E "(jupyter|openbb|uvicorn)" | grep -v grep
```

**Check ports in use:**
```bash
# Check if Jupyter is running (port 8888)
lsof -i :8888

# Check if API is running (port 8000)  
lsof -i :8000
```

### Log Files

Service logs are saved to your home directory:
- **Jupyter Lab**: `~/jupyter.log`
- **API Server**: `~/openbb_api.log`

**View logs:**
```bash
# Follow Jupyter logs
tail -f ~/jupyter.log

# Follow API logs  
tail -f ~/openbb_api.log

# View recent logs
cat ~/jupyter.log
cat ~/openbb_api.log
```

### Stopping Services

**Stop all services:**
```bash
./stop_all.sh
```

**Stop individual services:**
```bash
# Stop Jupyter (using your existing alias)
jstop

# Stop API server (if PID file exists)
kill $(cat ~/.openbb_api.pid)

# Force stop all OpenBB processes
pkill -f openbb
```

## Configuration

### Environment Variables

You can customize service behavior with environment variables:

**API Server:**
```bash
export OPENBB_API_HOST=0.0.0.0    # Default: 0.0.0.0
export OPENBB_API_PORT=8000       # Default: 8000  
export OPENBB_API_RELOAD=true     # Default: true
```

**Jupyter Lab:**
```bash
export JUPYTER_PORT=8888          # Default: 8888
export JUPYTER_IP=0.0.0.0         # Default: 0.0.0.0
```

### User Settings

OpenBB settings are stored in `~/.openbb_platform/user_settings.json`:

```json
{
  "credentials": {
    "fmp_api_key": "your_key",
    "polygon_api_key": "your_key",
    "benzinga_api_key": "your_key",
    "fred_api_key": "your_key"
  },
  "preferences": {
    "output_type": "OBBject"
  }
}
```

## Troubleshooting

### Common Issues

**1. Installation fails:**
```bash
# Check Python version
python3 --version  # Should be 3.9+

# Check Poetry installation
poetry --version

# Reinstall Poetry if needed
curl -sSL https://install.python-poetry.org | python3 -
```

**2. Services won't start:**
```bash
# Check if ports are already in use
lsof -i :8000  # API server
lsof -i :8888  # Jupyter

# Kill existing processes
./stop_all.sh
```

**3. Import errors:**
```bash
# Test OpenBB installation
python -c "from openbb import obb; print('✅ OpenBB imported successfully')"

# Check installed packages
pip list | grep openbb
```

**4. API keys not working:**
```bash
# Verify config file exists and has correct format
cat ~/.openbb_platform/user_settings.json

# Test API key in Python
python -c "from openbb import obb; print(obb.user.credentials.fmp_api_key)"
```

### Getting Help

**View service status:**
```bash
./start_all.sh  # Shows status of all services
```

**Check logs for errors:**
```bash
# Recent Jupyter errors
tail -20 ~/jupyter.log

# Recent API errors  
tail -20 ~/openbb_api.log
```

**Test basic functionality:**
```bash
# Test Python import
python -c "from openbb import obb; print(obb.equity.price.historical('AAPL').to_dataframe().head())"

# Test API endpoint
curl "http://localhost:8000/api/v1/equity/price/historical?symbol=AAPL"
```

## Development Workflow

### For Development Installation

If you chose development installation (`./install_openbb.sh` option 1):

**Key locations:**
- **Platform code**: `./openbb_platform/`
- **CLI code**: `./cli/`
- **Examples**: `./examples/`

**Making changes:**
1. Edit code in `openbb_platform/` or extensions
2. Changes are automatically available (editable install)
3. Restart services if needed: `./stop_all.sh && ./start_all.sh`

**Running tests:**
```bash
cd openbb_platform
pytest
```

### Data Provider Integration

**Available providers** (see `openbb_platform/providers/`):
- Free: Yahoo Finance, FRED, SEC, BLS, OECD
- Freemium: FMP, Polygon, Alpha Vantage
- Paid: Bloomberg, Benzinga, Intrinio

**Adding new providers:**
See development documentation in `openbb_platform/CONTRIBUTING.md`

## Post-Installation: Running the Application

After `./start_all.sh` successfully completes, you'll have access to multiple interfaces:

### 1. Web Interfaces

**Jupyter Lab** (Primary Development Environment)
- **URL**: http://localhost:8888
- **Purpose**: Interactive notebooks, data analysis, and development
- **Features**: 
  - Pre-loaded with OpenBB platform
  - Access to `alfa-class-env` kernel
  - Examples available in `./examples/` directory
  - Integration with existing Jupyter workflows

**REST API Documentation** (API Explorer)
- **URL**: http://localhost:8000/docs
- **Purpose**: Interactive API testing and documentation
- **Features**:
  - Try API endpoints directly in browser
  - View request/response schemas
  - Authentication setup for API keys

### 2. Programmatic Access

**Python SDK** (In Jupyter or scripts)
```python
from openbb import obb

# Get stock data
data = obb.equity.price.historical("AAPL", period="1y")
df = data.to_dataframe()
print(df.head())

# Get company profile
profile = obb.equity.profile("AAPL")
print(profile)
```

**REST API** (HTTP requests)
```bash
# Basic stock data
curl "http://localhost:8000/api/v1/equity/price/historical?symbol=AAPL&period=1y"

# Company fundamentals
curl "http://localhost:8000/api/v1/equity/fundamental/overview?symbol=AAPL"
```

### 3. Command Line Interface

**OpenBB CLI** (Terminal interface)
```bash
./start_cli.sh
```
Interactive terminal for financial data exploration.

### 4. Recommended Workflow

1. **Start with Jupyter Lab** (http://localhost:8888)
   - Open `examples/` folder for sample notebooks
   - Create new notebooks for your analysis
   - Use the `alfa-class-env` kernel

2. **Use API Documentation** (http://localhost:8000/docs)
   - Test endpoints before coding
   - Generate code snippets
   - Configure API authentication

3. **Monitor Services**
   ```bash
   # Check service status
   ./start_all.sh  # Shows current status
   
   # View logs
   tail -f ~/jupyter.log    # Jupyter output
   tail -f ~/openbb_api.log # API server output
   ```

4. **Stop Services When Done**
   ```bash
   ./stop_all.sh
   ```

### 5. Quick Start Examples

**Stock Analysis in Jupyter:**
1. Go to http://localhost:8888
2. Navigate to `examples/` folder
3. Open an existing notebook or create new one
4. Run:
   ```python
   from openbb import obb
   
   # Get Apple stock data
   stock_data = obb.equity.price.historical("AAPL", period="6m")
   df = stock_data.to_dataframe()
   
   # Plot the data
   import matplotlib.pyplot as plt
   df['close'].plot(title='AAPL Stock Price')
   plt.show()
   ```

**API Testing:**
1. Go to http://localhost:8000/docs
2. Find "equity" → "price" → "historical"
3. Click "Try it out"
4. Enter symbol: `AAPL`
5. Execute to see real data

## Next Steps

1. **Configure API keys** in `~/.openbb_platform/user_settings.json`
2. **Test installation**: `python -c "from openbb import obb; print(obb.equity.price.historical('AAPL'))"`
3. **Start services**: `./start_all.sh`
4. **Open Jupyter Lab**: http://localhost:8888
5. **Explore API docs**: http://localhost:8000/docs
6. **Check examples**: Navigate to `./examples/` in Jupyter

## Useful Resources

- **OpenBB Documentation**: https://docs.openbb.co/platform
- **API Reference**: https://docs.openbb.co/platform/reference  
- **GitHub Repository**: https://github.com/OpenBB-finance/OpenBB
- **Discord Community**: https://openbb.co/discord

---

**Happy investing with OpenBB! 🚀**