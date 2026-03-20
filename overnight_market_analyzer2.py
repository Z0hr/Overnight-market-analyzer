"""
Overnight Global Market to US Stock Correlation Analyzer
==========================================================
This application analyzes the conditional probability:
If a global market rises/falls by >X% overnight, how often does a US stock close green?

Author: Senior Python Developer & Quant Analyst
Tech Stack: Streamlit, yfinance, pandas, plotly
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pytz
from typing import Dict, Tuple
import warnings
import matplotlib
warnings.filterwarnings('ignore')

# CONFIGURATION & CONSTANTS
# 140 global markets with their Yahoo Finance tickers
GLOBAL_MARKETS = {
    # CRYPTOCURRENCIES (28 total)
    'Bitcoin': 'BTC-USD',
    'Ethereum': 'ETH-USD',
    'XRP': 'XRP-USD',
    'Solana': 'SOL-USD',
    'Cardano': 'ADA-USD',
    'Dogecoin': 'DOGE-USD',
    'Binance Coin': 'BNB-USD',
    'Avalanche': 'AVAX-USD',
    'Polkadot': 'DOT-USD',
    'Chainlink': 'LINK-USD',
    'Litecoin': 'LTC-USD',
    'Bitcoin Cash': 'BCH-USD',
    'Stellar': 'XLM-USD',
    'Uniswap': 'UNI-USD',
    'Cosmos': 'ATOM-USD',
    'Monero': 'XMR-USD',
    'Ethereum Classic': 'ETC-USD',
    'Filecoin': 'FIL-USD',
    'Hedera': 'HBAR-USD',
    'Aptos': 'APT-USD',
    'Arbitrum': 'ARB-USD',
    'Optimism': 'OP-USD',
    'Near Protocol': 'NEAR-USD',
    'VeChain': 'VET-USD',
    'Algorand': 'ALGO-USD',
    'Tezos': 'XTZ-USD',
    'Aave': 'AAVE-USD',
    'Injective': 'INJ-USD',

    # FOREX PAIRS (30 total)
    'EUR/USD': 'EURUSD=X',
    'USD/JPY': 'JPY=X',
    'GBP/USD': 'GBPUSD=X',
    'USD/CNY': 'USDCNY=X',
    'USD/CAD': 'CAD=X',
    'AUD/USD': 'AUDUSD=X',
    'USD/CHF': 'CHF=X',
    'NZD/USD': 'NZDUSD=X',
    'USD/HKD': 'HKD=X',
    'USD/SGD': 'SGD=X',
    'USD/SEK': 'SEK=X',
    'USD/NOK': 'NOK=X',
    'USD/DKK': 'DKK=X',
    'USD/MXN': 'MXN=X',
    'USD/BRL': 'BRL=X',
    'USD/ZAR': 'ZAR=X',
    'USD/INR': 'INR=X',
    'USD/KRW': 'KRW=X',
    'USD/TRY': 'TRY=X',
    'USD/RUB': 'RUB=X',
    'USD/PLN': 'PLN=X',
    'USD/THB': 'THB=X',
    'USD/IDR': 'IDR=X',
    'USD/MYR': 'MYR=X',
    'USD/PHP': 'PHP=X',
    'EUR/GBP': 'EURGBP=X',
    'EUR/JPY': 'EURJPY=X',
    'EUR/CHF': 'EURCHF=X',
    'GBP/JPY': 'GBPJPY=X',
    'AUD/JPY': 'AUDJPY=X',

    # GLOBAL EQUITY INDICES (43 total)
    # USA
    'S&P 500': '^GSPC',
    'Dow Jones': '^DJI',
    'Nasdaq Composite': '^IXIC',
    'Russell 2000': '^RUT',
    'S&P 400 (Mid-Cap)': '^MID',
    'NYSE Composite': '^NYA',
    'Nasdaq 100': '^NDX',
    'Dow Jones Transport': '^DJT',
    'Dow Jones Utilities': '^DJU',
    'CBOE Volatility (VIX)': '^VIX',

    # EUROPE
    'Germany (DAX)': '^GDAXI',
    'France (CAC 40)': '^FCHI',
    'London (FTSE)': '^FTSE',
    'Euronext 100': '^N100',
    'Spain (IBEX 35)': '^IBEX',
    'Italy (FTSE MIB)': 'FTSEMIB.MI',
    'Netherlands (AEX)': '^AEX',
    'Switzerland (SMI)': '^SSMI',
    'Sweden (OMX Stockholm)': '^OMX',
    'Belgium (BEL 20)': '^BFX',
    'Austria (ATX)': '^ATX',
    'Denmark (OMX Copenhagen)': '^OMXC25',

    # ASIA PACIFIC
    'Tokyo (Nikkei)': '^N225',
    'Hong Kong (HSI)': '^HSI',
    'India (Nifty 50)': '^NSEI',
    'Australia (ASX 200)': '^AXJO',
    'South Korea (KOSPI)': '^KS11',
    'Shanghai Composite': '000001.SS',
    'Shenzhen Component': '399001.SZ',
    'Taiwan (TAIEX)': '^TWII',
    'Singapore (STI)': '^STI',
    'Indonesia (IDX)': '^JKSE',
    'Malaysia (KLCI)': '^KLSE',
    'Thailand (SET)': '^SET.BK',
    'India (BSE Sensex)': '^BSESN',
    'New Zealand (NZX 50)': '^NZ50',

    # AMERICAS
    'Canada (S&P/TSX)': '^GSPTSE',
    'Brazil (Bovespa)': '^BVSP',
    'Mexico (IPC)': '^MXX',
    'Argentina (MERVAL)': '^MERV',

    # MIDDLE EAST & AFRICA
    'Saudi Arabia (Tadawul)': '^TASI.SR',
    'South Africa (JSE)': '^J203.JO',
    'Egypt (EGX 30)': '^CASE30',

    # COMMODITIES (24 total)
    # ENERGY
    'Crude Oil (WTI)': 'CL=F',
    'Brent Crude Oil': 'BZ=F',
    'Natural Gas': 'NG=F',
    'Heating Oil': 'HO=F',
    'RBOB Gasoline': 'RB=F',

    # METALS
    'Gold': 'GC=F',
    'Silver': 'SI=F',
    'Platinum': 'PL=F',
    'Palladium': 'PA=F',
    'Copper': 'HG=F',
    'Aluminum': 'ALI=F',
    'Zinc': 'ZNC=F',

    # AGRICULTURE
    'Corn': 'ZC=F',
    'Wheat': 'ZW=F',
    'Soybeans': 'ZS=F',
    'Soybean Oil': 'ZL=F',
    'Soybean Meal': 'ZM=F',
    'Live Cattle': 'LE=F',
    'Lean Hogs': 'HE=F',
    'Feeder Cattle': 'GF=F',
    'Coffee': 'KC=F',
    'Cocoa': 'CC=F',
    'Sugar': 'SB=F',
    'Cotton': 'CT=F',

    # US SECTOR ETFs & BOND/RATE BENCHMARKS (15 total)
    # SPDR Sector ETFs
    'Energy Select SPDR (XLE)': 'XLE',
    'Financial Select SPDR (XLF)': 'XLF',
    'Technology Select SPDR (XLK)': 'XLK',
    'Health Care Select SPDR (XLV)': 'XLV',
    'Consumer Disc. SPDR (XLY)': 'XLY',
    'Consumer Staples SPDR (XLP)': 'XLP',
    'Industrials Select SPDR (XLI)': 'XLI',
    'Materials Select SPDR (XLB)': 'XLB',
    'Utilities Select SPDR (XLU)': 'XLU',
    'Real Estate SPDR (XLRE)': 'XLRE',

    # BOND & RATE BENCHMARKS
    'US 10-Year Treasury Yield': '^TNX',
    'US 30-Year Treasury Yield': '^TYX',
    'US 5-Year Treasury Yield': '^FVX',
    'US 2-Year Treasury Yield': '^IRX',
    'iShares 20+ Yr Treasury (TLT)': 'TLT',
}

# US Eastern Timezone
ET = pytz.timezone('US/Eastern')

# DATA FETCHING & PROCESSING FUNCTIONS

@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_market_data(ticker: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
    """
    Fetch historical market data from Yahoo Finance.
    
    Args:
        ticker: Yahoo Finance ticker symbol
        start_date: Start date for data fetch
        end_date: End date for data fetch
    
    Returns:
        DataFrame with OHLC data, or empty DataFrame if fetch fails
    """
    try:
        # Fetch data with a buffer (extra days) to ensure we have previous close
        buffer_start = start_date - timedelta(days=5)
        data = yf.download(ticker, start=buffer_start, end=end_date, progress=False)
        
        if data.empty:
            st.warning(f"No data available for {ticker}")
            return pd.DataFrame()
        
        # Handle multi-level columns (from yfinance)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        
        return data
    
    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {str(e)}")
        return pd.DataFrame()


def calculate_overnight_move(data: pd.DataFrame) -> pd.Series:
    """
    Calculate the overnight percentage move for a market.
    
    Overnight Move = (Current Open - Previous Close) / Previous Close * 100
    
    This approximates the move from 4:00 PM ET (previous day) to 9:30 AM ET (current day).
    
    Args:
        data: DataFrame with OHLC data
    
    Returns:
        Series with overnight percentage moves
    """
    if data.empty or 'Open' not in data.columns or 'Close' not in data.columns:
        return pd.Series(dtype=float)
    
    # Calculate: (Today's Open - Yesterday's Close) / Yesterday's Close * 100
    overnight_move = ((data['Open'] - data['Close'].shift(1)) / data['Close'].shift(1)) * 100
    
    return overnight_move


def calculate_intraday_move(data: pd.DataFrame) -> pd.Series:
    """
    Calculate whether the stock closed higher than it opened (Green day).
    
    Args:
        data: DataFrame with OHLC data
    
    Returns:
        Series with boolean values (True = Close > Open)
    """
    if data.empty or 'Open' not in data.columns or 'Close' not in data.columns:
        return pd.Series(dtype=bool)
    
    # True if stock closed higher than it opened
    return data['Close'] > data['Open']


def analyze_market_correlation(
    market_data: pd.DataFrame,
    stock_data: pd.DataFrame,
    threshold: float,
    direction: str = "Increase"
) -> Tuple[int, int, float]:
    """
    Analyze the correlation between market overnight move and stock intraday performance.
    
    Logic:
    1. Calculate overnight move for the global market
    2. Filter days where overnight move exceeds threshold in the chosen direction
    3. For those days, check if the US stock closed green
    4. Calculate success rate
    
    Args:
        market_data: Global market OHLC data
        stock_data: US stock OHLC data
        threshold: Minimum overnight move percentage magnitude to consider
        direction: "Increase" to filter days up >threshold%, "Decrease" for days down >threshold%
    
    Returns:
        Tuple of (total_occurrences, green_days, success_rate)
    """
    if market_data.empty or stock_data.empty:
        return 0, 0, 0.0
    
    # Calculate overnight move for the global market
    market_overnight = calculate_overnight_move(market_data)
    
    # Calculate intraday performance for the US stock
    stock_green_days = calculate_intraday_move(stock_data)
    
    # Align the data on dates (inner join to get common trading days)
    aligned_data = pd.DataFrame({
        'market_overnight': market_overnight,
        'stock_green': stock_green_days
    }).dropna()
    
    # Filter based on direction
    if direction == "Increase":
        filtered_days = aligned_data[aligned_data['market_overnight'] > threshold]
    else:  # Decrease
        filtered_days = aligned_data[aligned_data['market_overnight'] < -threshold]
    
    total_occurrences = len(filtered_days)
    
    if total_occurrences == 0:
        return 0, 0, 0.0
    
    # Count how many of those days the stock closed green
    green_days = filtered_days['stock_green'].sum()
    
    # Calculate success rate
    success_rate = (green_days / total_occurrences) * 100
    
    return total_occurrences, int(green_days), success_rate

# VISUALIZATION FUNCTIONS

def create_results_dataframe(results: Dict) -> pd.DataFrame:
    """
    Create a formatted DataFrame from analysis results.
    
    Args:
        results: Dictionary with market names as keys and analysis results as values
    
    Returns:
        Formatted DataFrame for display
    """
    data = []
    for market, (total, green, success_rate) in results.items():
        data.append({
            'Market': market,
            'Total Signals': total,
            'Green Days': green,
            'Success Rate (%)': round(success_rate, 2)
        })
    
    df = pd.DataFrame(data)
    df = df.sort_values('Success Rate (%)', ascending=False)
    
    return df


def create_bar_chart(results_df: pd.DataFrame) -> go.Figure:
    """
    Create an interactive bar chart showing success rates by market.
    
    Args:
        results_df: DataFrame with analysis results
    
    Returns:
        Plotly figure object
    """
    # Filter out markets with no signals
    df_filtered = results_df[results_df['Total Signals'] > 0].copy()
    
    if df_filtered.empty:
        # Return empty figure with message
        fig = go.Figure()
        fig.add_annotation(
            text="No data available for the selected parameters",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        return fig
    
    # Create bar chart
    fig = go.Figure()
    
    # Add bars with color gradient based on success rate
    fig.add_trace(go.Bar(
        x=df_filtered['Market'],
        y=df_filtered['Success Rate (%)'],
        text=df_filtered['Success Rate (%)'].apply(lambda x: f'{x:.1f}%'),
        textposition='outside',
        marker=dict(
            color=df_filtered['Success Rate (%)'],
            colorscale='RdYlGn',
            cmin=0,
            cmax=100,
            colorbar=dict(title="Success Rate (%)")
        ),
        hovertemplate='<b>%{x}</b><br>' +
                      'Success Rate: %{y:.2f}%<br>' +
                      'Total Signals: %{customdata}<br>' +
                      '<extra></extra>',
        customdata=df_filtered['Total Signals']
    ))
    
    # Add horizontal line at 50% (random chance)
    fig.add_hline(
        y=50, 
        line_dash="dash", 
        line_color="gray",
        annotation_text="50% (Random)",
        annotation_position="right"
    )
    
    # Update layout
    fig.update_layout(
        title='Success Rate by Global Market',
        xaxis_title='Global Market',
        yaxis_title='Success Rate (%)',
        yaxis=dict(range=[0, 100]),
        template='plotly_white',
        height=500,
        showlegend=False
    )
    
    return fig

# STREAMLIT APP

def main():
    """Main Streamlit application."""
    
    # Page configuration
    st.set_page_config(
        page_title="Overnight Market Analyzer",
        page_icon="📈",
        layout="wide"
    )
    
    # Title and description
    st.title("📈 Overnight Global Market → US Stock Analyzer")
    st.markdown("""
    This tool analyzes the **conditional probability**: If a global market moves by more than X%
    overnight (up **or** down), how often does your chosen US stock close higher than it opened?
    
    **Overnight Move**: Approximated as `(Current Open - Previous Close) / Previous Close`  
    **Intraday Performance**: `Close > Open` (Green day)
    """)
    
    # Sidebar for inputs
    st.sidebar.header("⚙️ Configuration")
    
    # User inputs
    stock_ticker = st.sidebar.text_input(
        "US Stock Ticker",
        value="VOO",
        help="Enter a valid US stock ticker (e.g., VOO, SPY, AAPL)"
    ).upper()
    
    # Date range
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=datetime.now() - timedelta(days=365),
            max_value=datetime.now()
        )
    with col2:
        end_date = st.date_input(
            "End Date",
            value=datetime.now(),
            max_value=datetime.now()
        )
    
    # Direction toggle
    direction = st.sidebar.radio(
        "Overnight Move Direction",
        options=["Increase", "Decrease"],
        index=0,
        help="Increase: filter days where the market gapped UP by more than X%\nDecrease: filter days where the market gapped DOWN by more than X%",
        horizontal=True
    )

    direction_symbol = "📈" if direction == "Increase" else "📉"
    direction_label = "rise" if direction == "Increase" else "fall"

    # Threshold
    threshold = st.sidebar.number_input(
        f"Overnight Move Threshold (%)",
        min_value=0.0,
        max_value=20.0,
        value=1.0,
        step=0.1,
        help=f"The market must {direction_label} by more than this % overnight to count as a signal"
    )
    
    # Run analysis button
    analyze_button = st.sidebar.button("🔍 Run Analysis", type="primary")
    
    # Display market list
    with st.sidebar.expander("📊 Markets Analyzed"):
        for name, ticker in GLOBAL_MARKETS.items():
            st.text(f"• {name}: {ticker}")
    
    # Main analysis
    if analyze_button:
        if start_date >= end_date:
            st.error("❌ Start date must be before end date!")
            return
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Fetch US stock data
        status_text.text(f"Fetching data for {stock_ticker}...")
        stock_data = fetch_market_data(stock_ticker, start_date, end_date)
        
        if stock_data.empty:
            st.error(f"❌ Could not fetch data for {stock_ticker}. Please check the ticker symbol.")
            return
        
        progress_bar.progress(10)
        
        # Analyze each global market
        results = {}
        total_markets = len(GLOBAL_MARKETS)
        
        for idx, (market_name, market_ticker) in enumerate(GLOBAL_MARKETS.items()):
            status_text.text(f"Analyzing {market_name}...")
            
            # Fetch market data
            market_data = fetch_market_data(market_ticker, start_date, end_date)
            
            if not market_data.empty:
                # Perform correlation analysis
                total, green, success_rate = analyze_market_correlation(
                    market_data, stock_data, threshold, direction
                )
                results[market_name] = (total, green, success_rate)
            else:
                results[market_name] = (0, 0, 0.0)
            
            # Update progress
            progress = 10 + int((idx + 1) / total_markets * 90)
            progress_bar.progress(progress)
        
        status_text.text("Analysis complete!")
        progress_bar.progress(100)
        
        # Clear progress indicators
        import time
        time.sleep(0.5)
        progress_bar.empty()
        status_text.empty()
        
        # Display results
        st.success("✅ Analysis Complete!")
        
        # Create results dataframe
        results_df = create_results_dataframe(results)
        
        # Display summary statistics
        st.header(f"📊 Summary Statistics — {direction_symbol} {direction} Mode")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Analysis Period",
                f"{(end_date - start_date).days} days"
            )
        with col2:
            st.metric(
                "Stock Analyzed",
                stock_ticker
            )
        with col3:
            total_signals = results_df['Total Signals'].sum()
            st.metric(
                "Total Signals",
                total_signals
            )
        with col4:
            avg_success = results_df[results_df['Total Signals'] > 0]['Success Rate (%)'].mean()
            st.metric(
                "Avg Success Rate",
                f"{avg_success:.1f}%" if not pd.isna(avg_success) else "N/A"
            )
        
        # Display results table
        st.header("📋 Detailed Results")
        st.dataframe(
            results_df.style.background_gradient(
                subset=['Success Rate (%)'],
                cmap='RdYlGn',
                vmin=0,
                vmax=100
            ).format({
                'Total Signals': '{:,.0f}',
                'Green Days': '{:,.0f}',
                'Success Rate (%)': '{:.2f}%'
            }),
            use_container_width=True,
            hide_index=True
        )
        
        # Display chart
        st.header("📈 Visual Analysis")
        fig = create_bar_chart(results_df)
        st.plotly_chart(fig, use_container_width=True)
        
        # Insights
        st.header("💡 Key Insights")
        
        # Find best performing market
        best_market = results_df[results_df['Total Signals'] > 0].nlargest(1, 'Success Rate (%)')
        if not best_market.empty:
            st.info(f"""
            **Best Performing Market**: {best_market.iloc[0]['Market']}  
            - Success Rate: {best_market.iloc[0]['Success Rate (%)']:.2f}%  
            - Total Signals: {best_market.iloc[0]['Total Signals']:.0f}  
            - Green Days: {best_market.iloc[0]['Green Days']:.0f}
            """)
        
        # Statistical significance note
        st.warning("""
        **Note on Statistical Significance**: Markets with fewer than 30 signals may not provide 
        statistically significant results. Consider increasing your date range or lowering the threshold 
        for more robust analysis.
        """)
        
    else:
        # Display instructions when no analysis has been run
        st.info("👈 Configure your parameters in the sidebar and click **Run Analysis** to begin!")
        
        # Display example use case
        st.markdown("### 📖 How to Use This Tool")
        st.markdown("""
        1. **Select a US Stock**: Enter the ticker symbol (e.g., VOO, SPY, AAPL)
        2. **Choose Date Range**: Select the analysis period
        3. **Set Direction**: Choose whether to analyze overnight **increases** or **decreases**
        4. **Set Threshold**: Define the minimum overnight move magnitude (e.g., 1% = market moved >1%)
        5. **Run Analysis**: Click the button to analyze correlations
        
        #### Example Insights:
        - 📈 If Bitcoin **rises** >2% overnight, does VOO tend to close green?
        - 📉 If the Nikkei **falls** >1% overnight, does AAPL tend to close red?
        - How does EUR/USD overnight weakness correlate with tech stock performance?
        - Which global market drop is the strongest predictor for your stock's intraday moves?
        """)

# ENTRY POINT

if __name__ == "__main__":
    main()
