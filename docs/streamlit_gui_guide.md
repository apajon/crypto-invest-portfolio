# Streamlit GUI Usage Guide

## Overview

The crypto portfolio application now includes a modern web-based GUI built with Streamlit, providing an intuitive interface for managing your cryptocurrency investments.

## Getting Started

### Installation

The Streamlit GUI is automatically available after installing the project dependencies:

```bash
poetry install
```

### Running the GUI

Start the Streamlit application using one of these methods:

1. **Using the Poetry script** (recommended):
   ```bash
   poetry run crypto-portfolio-gui
   ```

2. **Direct execution**:
   ```bash
   poetry run streamlit run src/crypto_invest_portfolio/streamlit_gui/main.py
   ```

3. **Manual execution**:
   ```bash
   cd src/crypto_invest_portfolio/streamlit_gui
   poetry run streamlit run main.py
   ```

The application will open in your default web browser at `http://localhost:8501`.

## Features

### 🌐 Multi-Language Support
- Switch between English and French
- Language selection in sidebar
- Persistent language settings

### 📊 Portfolio Management
- **View Portfolio**: Overview of all investments with key metrics
- **Add Purchase**: Add new cryptocurrency purchases
- **Add Staking**: Record staking rewards and gains
- **Edit/Delete**: Modify or remove existing entries
- **Wallet Filtering**: Filter portfolio by specific wallets

### 📈 Analysis & Insights
- **Single Analysis**: One-time portfolio performance analysis
- **Auto-Update**: Continuous monitoring with configurable intervals
- **Portfolio Summary**: Visual metrics and statistics
- **Wallet Grouping**: Analyze performance by wallet

### 📉 Visualizations
- **Coin History**: Price charts for individual cryptocurrencies
- **Portfolio Charts**: Distribution by coin, wallet, and type
- **Investment Timeline**: Track investment growth over time
- **Interactive Plots**: Matplotlib integration with Streamlit

### ⚙️ Settings & Management
- **Language Configuration**: Switch interface language
- **Database Management**: View schema, export data, optimize database
- **Application Info**: Technical details and version information

## Navigation

The application uses a sidebar navigation system:

1. **Portfolio View** - Main dashboard and portfolio overview
2. **Add Purchase** - Form to add new cryptocurrency purchases
3. **Add Staking** - Form to record staking gains
4. **Edit/Delete** - Manage existing portfolio entries
5. **Analysis** - Portfolio performance analysis tools
6. **Visualization** - Charts and graphs
7. **Settings** - Application configuration

## Usage Examples

### Adding a Purchase

1. Navigate to "Add Purchase" in the sidebar
2. Fill in the form:
   - Coin name (e.g., "Bitcoin")
   - Symbol (e.g., "BTC")
   - Amount purchased
   - Buy price in CAD
   - Fees (buy/sell percentages)
   - Coin type (classic/risk/stable)
   - Wallet name
3. Click "Add Purchase"
4. Confirm the success message

### Running Analysis

1. Go to "Analysis" page
2. Choose "Single Analysis" or "Auto-Update"
3. Optionally enable "Group by Wallet"
4. Click "Analyze Portfolio" to generate insights
5. View results in the interface and console

### Viewing Charts

1. Navigate to "Visualization"
2. Choose between:
   - **Coin History Plot**: Price charts for specific coins
   - **Portfolio Charts**: Distribution and composition charts
3. Configure options and generate visualizations

## Data Management

### Database

- All data is stored in a local SQLite database (`crypto_portfolio.db`)
- Database is automatically initialized on first run
- Use Settings page to view schema and manage data

### Export Data

1. Go to Settings page
2. Click "Export Portfolio Data"
3. Download JSON file with all portfolio data

### Language Settings

1. Use the language selector in the sidebar for quick switching
2. Or go to Settings > Language Settings for detailed configuration

## Integration with CLI

The Streamlit GUI and CLI application share the same:
- Database
- Configuration files
- Analysis functions
- Language settings

You can use both interfaces interchangeably without conflicts.

## Troubleshooting

### Common Issues

1. **Port already in use**: Change the port with `--server.port XXXX`
2. **Database errors**: Check file permissions for `crypto_portfolio.db`
3. **Import errors**: Ensure all dependencies are installed with `poetry install`

### Getting Help

- Check the console output for detailed error messages
- Verify Python and package versions in Settings > Application Info
- Ensure CoinGecko API is accessible for price data

## Performance Tips

- Use auto-update sparingly to avoid API rate limits
- Export data regularly as backup
- Use database vacuum function periodically to optimize performance

## Browser Compatibility

Tested and compatible with:
- Chrome/Chromium (recommended)
- Firefox
- Safari
- Edge

For best experience, use a modern browser with JavaScript enabled.
