"""
Overnight Global Market to US Stock Correlation Analyzer
==========================================================
This application analyzes the conditional probability:
If a global market rises/falls by >X% overnight, how often does a US stock close green?

Author: Z0hr
Tech Stack: Streamlit, yfinance, pandas, plotly
"""

import time                                   # FIX: was imported inside main()
import warnings
from datetime import datetime, timedelta
from typing import Dict, Tuple

import matplotlib                             # Required by pandas .style.background_gradient()
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

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

# Minimum signal count for a statistically meaningful result.
# Used in both the Key Insights filter and UI warning message.
MIN_SIGNALS = 30

# DATA FETCHING & PROCESSING

def _download_ticker(ticker: str, start_date, end_date) -> pd.DataFrame:
    """
    Raw yfinance download for a single ticker — NO caching.

    Keeping the actual network call in an uncached function ensures that
    fetch_with_retry can make genuine new HTTP requests on each attempt
    instead of getting the same cached empty DataFrame back every time.

    Args:
        ticker:     Yahoo Finance ticker symbol.
        start_date: Start of the fetch window (date or datetime).
        end_date:   End of the fetch window (date or datetime).

    Returns:
        DataFrame with flat, 1-D OHLC columns, or empty DataFrame on failure.
    """
    try:
        # 5-day buffer guarantees a prior close for the first requested day
        # even across long weekends and public holidays.
        buffer_start = start_date - timedelta(days=5)
        data = yf.download(
            ticker,
            start=buffer_start,
            end=end_date,
            progress=False,
            auto_adjust=True,
        )

        if data.empty:
            return pd.DataFrame()

        # yfinance >=1.x wraps single-ticker downloads in MultiIndex columns
        # e.g. ('Close', 'AAPL') -> 'Close'
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        # Drop duplicate column names that can appear after the flatten
        data = data.loc[:, ~data.columns.duplicated()]

        # Coerce every OHLC column to a plain 1-D float Series.
        # yfinance 1.x can leave these as DataFrame-like objects, which causes
        # pd.DataFrame({...}) to raise AssertionError downstream.
        for col in ('Open', 'High', 'Low', 'Close', 'Volume'):
            if col in data.columns:
                data[col] = pd.to_numeric(data[col].squeeze(), errors='coerce')

        return data

    except Exception as e:
        err = str(e).lower()
        # Rate-limit hits are expected when scanning 140 markets; silence them.
        if 'rate' in err or '429' in err or 'too many' in err:
            return pd.DataFrame()
        st.warning(f"Could not fetch {ticker}: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def fetch_market_data(ticker: str, start_date, end_date) -> pd.DataFrame:
    """
    Cached wrapper around _download_ticker.

    Used by fetch_all_market_data for the 140-market background scan.
    Do NOT call this from fetch_with_retry — the cache would swallow retries.
    """
    return _download_ticker(ticker, start_date, end_date)



def fetch_with_retry(ticker: str, start_date, end_date, retries: int = 3) -> pd.DataFrame:
    """
    Retry the stock ticker fetch with exponential backoff.

    IMPORTANT: calls _download_ticker (uncached), NOT fetch_market_data.
    If we called the cached version, a rate-limit-induced empty result would be
    stored in the cache and every subsequent "retry" would just return that same
    empty DataFrame instantly — the sleep would never help.

    Args:
        ticker:     Yahoo Finance ticker symbol.
        start_date: Start of the fetch window.
        end_date:   End of the fetch window.
        retries:    Maximum number of attempts before giving up.

    Returns:
        DataFrame on success, or empty DataFrame after all retries exhausted.
    """
    for attempt in range(1, retries + 1):
        data = _download_ticker(ticker, start_date, end_date)  # bypass cache
        if not data.empty:
            return data
        if attempt < retries:
            wait = 2 ** attempt  # 2s, 4s, 8s
            time.sleep(wait)
    return pd.DataFrame()


def _parse_bulk_ticker(bulk: pd.DataFrame, ticker: str) -> pd.DataFrame:
    """
    Extract and clean one ticker's OHLCV slice from a bulk yf.download result.

    yfinance returns a MultiIndex DataFrame when given multiple tickers:
      level 0 = Price field ('Open', 'Close', …)
      level 1 = Ticker symbol

    Args:
        bulk:   Full multi-ticker DataFrame from yf.download.
        ticker: The individual ticker to extract.

    Returns:
        Clean single-ticker DataFrame, or empty DataFrame on failure.
    """
    try:
        if isinstance(bulk.columns, pd.MultiIndex):
            # xs selects across level 1 (Ticker) and returns all price fields
            df = bulk.xs(ticker, axis=1, level=1).copy()
        else:
            # Single-ticker fallback — columns are already flat
            df = bulk.copy()

        if df.empty:
            return pd.DataFrame()

        df = df.loc[:, ~df.columns.duplicated()]
        for col in ('Open', 'High', 'Low', 'Close', 'Volume'):
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].squeeze(), errors='coerce')
        return df

    except Exception:
        return pd.DataFrame()


# Number of tickers per bulk download request.
# 50 is a safe ceiling — large enough to slash API calls, small enough to avoid
# URL-length or timeout issues with Yahoo Finance.
BULK_BATCH_SIZE = 50


@st.cache_data(ttl=3600)
def fetch_all_market_data(start_date, end_date) -> Dict[str, pd.DataFrame]:
    """
    Download all 140 global market tickers using yfinance bulk requests.

    Instead of firing 140 individual HTTP requests (the old approach, even with
    a thread pool), this splits the tickers into batches of BULK_BATCH_SIZE and
    downloads each batch in a single yf.download call.  140 tickers → 3 calls.

    A 1-second pause between batches prevents the remaining small number of
    requests from triggering Yahoo Finance's rate limiter.

    Args:
        start_date: Start of the fetch window.
        end_date:   End of the fetch window.

    Returns:
        {market_name: DataFrame} — empty DataFrame for any failed ticker.
    """
    buffer_start = start_date - timedelta(days=5)
    items        = list(GLOBAL_MARKETS.items())
    result: Dict[str, pd.DataFrame] = {}

    for batch_start in range(0, len(items), BULK_BATCH_SIZE):
        batch       = items[batch_start : batch_start + BULK_BATCH_SIZE]
        batch_names = [name   for name, _      in batch]
        batch_ticks = [ticker for _,    ticker in batch]

        try:
            bulk = yf.download(
                batch_ticks,
                start=buffer_start,
                end=end_date,
                progress=False,
                auto_adjust=True,
            )

            if bulk.empty:
                for name in batch_names:
                    result[name] = pd.DataFrame()
            else:
                for name, ticker in batch:
                    result[name] = _parse_bulk_ticker(bulk, ticker)

        except Exception:
            for name in batch_names:
                result[name] = pd.DataFrame()

        # Brief pause between batches — 3 calls total means this adds ≤2s
        if batch_start + BULK_BATCH_SIZE < len(items):
            time.sleep(1)

    return result


def calculate_overnight_move(data: pd.DataFrame) -> pd.Series:
    """
    Overnight Move = (Today Open - Yesterday Close) / Yesterday Close * 100

    Approximates the gap from 4:00 PM ET (prior close) to 9:30 AM ET (open).

    Returns:
        Float Series indexed by date, or empty Series if data is invalid.
    """
    if data.empty or 'Open' not in data.columns or 'Close' not in data.columns:
        return pd.Series(dtype=float)

    open_  = data['Open'].squeeze()
    close_ = data['Close'].squeeze()
    return ((open_ - close_.shift(1)) / close_.shift(1) * 100).squeeze()


def calculate_intraday_move(data: pd.DataFrame) -> pd.Series:
    """
    Returns a boolean Series: True on days the stock closed above its open.

    Returns:
        Boolean Series, or empty Series if data is invalid.
    """
    if data.empty or 'Open' not in data.columns or 'Close' not in data.columns:
        return pd.Series(dtype=bool)

    return data['Close'].squeeze() > data['Open'].squeeze()


def analyze_market_correlation(
    market_data: pd.DataFrame,
    stock_green_days: pd.Series,
    threshold: float,
    direction: str = "Increase",
) -> Tuple[int, int, float]:
    """
    Compute P(stock closes green | market overnight move exceeds threshold).

    Args:
        market_data:      Global market OHLC DataFrame.
        stock_green_days: Pre-computed boolean Series (Close > Open) for the
                          target stock.  Passed in to avoid recomputing it
                          once per market (140x redundant calls previously).
        threshold:        Minimum overnight move magnitude (absolute %).
        direction:        "Increase" for gap-up days; "Decrease" for gap-down.

    Returns:
        (total_occurrences, green_days, success_rate_percent)
    """
    if market_data.empty or stock_green_days.empty:
        return 0, 0, 0.0

    market_overnight = calculate_overnight_move(market_data)

    aligned = pd.DataFrame({
        'market_overnight': market_overnight.squeeze(),
        'stock_green':      stock_green_days.squeeze(),
    }).dropna()

    if aligned.empty:
        return 0, 0, 0.0

    mask = (
        aligned['market_overnight'] > threshold
        if direction == "Increase"
        else aligned['market_overnight'] < -threshold
    )
    filtered = aligned[mask]

    total = len(filtered)
    if total == 0:
        return 0, 0, 0.0

    green        = int(filtered['stock_green'].sum())
    success_rate = green / total * 100
    return total, green, success_rate

# VISUALISATION

def create_results_dataframe(results: Dict) -> pd.DataFrame:
    """
    Build a display-ready DataFrame from the correlation results dict.

    Args:
        results: {market_name: (total, green, success_rate)}

    Returns:
        DataFrame sorted by success rate descending.
    """
    df = pd.DataFrame([
        {
            'Market':           market,
            'Total Signals':    total,
            'Green Days':       green,
            'Success Rate (%)': round(success_rate, 2),
        }
        for market, (total, green, success_rate) in results.items()
    ])
    return df.sort_values('Success Rate (%)', ascending=False)


def create_bar_chart(results_df: pd.DataFrame) -> go.Figure:
    """
    Interactive Plotly bar chart of per-market success rates.

    Args:
        results_df: Output of create_results_dataframe().

    Returns:
        Plotly Figure.
    """
    df = results_df[results_df['Total Signals'] > 0].copy()

    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available for the selected parameters",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16),
        )
        return fig

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df['Market'],
        y=df['Success Rate (%)'],
        text=df['Success Rate (%)'].apply(lambda x: f'{x:.1f}%'),
        textposition='outside',
        marker=dict(
            color=df['Success Rate (%)'],
            colorscale='RdYlGn',
            cmin=0,
            cmax=100,
            colorbar=dict(title="Success Rate (%)"),
        ),
        hovertemplate=(
            '<b>%{x}</b><br>'
            'Success Rate: %{y:.2f}%<br>'
            'Total Signals: %{customdata}<br>'
            '<extra></extra>'
        ),
        customdata=df['Total Signals'],
    ))
    fig.add_hline(
        y=50,
        line_dash="dash",
        line_color="gray",
        annotation_text="50% (Random)",
        annotation_position="right",
    )
    fig.update_layout(
        title='Success Rate by Global Market',
        xaxis_title='Global Market',
        yaxis_title='Success Rate (%)',
        yaxis=dict(range=[0, 110]),  # extra headroom for outside text labels
        template='plotly_white',
        height=500,
        showlegend=False,
    )
    return fig

# STREAMLIT APP

def main() -> None:
    """Main Streamlit application entry point."""

    st.set_page_config(
        page_title="Overnight Market Analyzer",
        page_icon="📈",
        layout="wide",
    )

    st.title("Overnight Global Market → US Stock Analyzer")
    st.markdown("""
    This tool analyzes the **conditional probability**: If a global market moves by more than X%
    overnight (up **or** down), how often does your chosen US stock close higher than it opened?

    **Overnight Move**: Approximated as `(Current Open − Previous Close) / Previous Close`
    **Intraday Performance**: `Close > Open` (Green day)
    """)

    st.sidebar.header("Configuration")

    stock_ticker = st.sidebar.text_input(
        "US Stock Ticker",
        value="VOO",
        help="Enter a valid US stock ticker (e.g., VOO, SPY, AAPL)",
    ).upper()

    # FIX: compute today once — previously datetime.now() was called 4 separate times
    today = datetime.now()

    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=today - timedelta(days=365),
            max_value=today,
        )
    with col2:
        end_date = st.date_input(
            "End Date",
            value=today,
            max_value=today,
        )

    direction = st.sidebar.radio(
        "Overnight Move Direction",
        options=["Increase", "Decrease"],
        index=0,
        help=(
            "Increase: filter days where the market gapped UP by more than X%\n"
            "Decrease: filter days where the market gapped DOWN by more than X%"
        ),
        horizontal=True,
    )

    direction_symbol = "📈" if direction == "Increase" else "📉"
    direction_label  = "rise" if direction == "Increase" else "fall"

    # FIX: removed spurious f-string prefix (no interpolation in the label itself)
    threshold = st.sidebar.number_input(
        "Overnight Move Threshold (%)",
        min_value=0.0,
        max_value=20.0,
        value=1.0,
        step=0.1,
        help=f"The market must {direction_label} by more than this % overnight to count as a signal",
    )

    analyze_button = st.sidebar.button("Run Analysis", type="primary")

    with st.sidebar.expander("Markets Analyzed"):
        for name, ticker in GLOBAL_MARKETS.items():
            st.text(f"• {name}: {ticker}")

    if analyze_button:
        if start_date >= end_date:
            st.error("Start date must be before end date!")
            return

        progress_bar = st.progress(0)
        status_text  = st.empty()

        # Step 1: fetch target stock (10% of bar)
        status_text.text(f"Fetching data for {stock_ticker}...")
        stock_data = fetch_with_retry(stock_ticker, start_date, end_date)

        if stock_data.empty:
            st.error(
                f"Could not fetch data for **{stock_ticker}** after multiple attempts. "
                "This is usually caused by Yahoo Finance rate limiting — please wait "
                "30 seconds and try again. If the problem persists, double-check the ticker symbol."
            )
            return

        progress_bar.progress(10)

        # Step 2: pre-compute stock green-day series ONCE
        # Previously this was recomputed inside analyze_market_correlation on
        # every iteration — 140 redundant calls for the same stock_data.
        stock_green_days = calculate_intraday_move(stock_data)

        # Step 3: fetch all market data via bulk download (10% -> 70%)
        status_text.text("Fetching all market data (bulk download)…")
        all_market_data = fetch_all_market_data(start_date, end_date)
        progress_bar.progress(70)

        # Step 4: correlation analysis (70% -> 100%)
        results       = {}
        total_markets = len(GLOBAL_MARKETS)

        for idx, (market_name, market_data) in enumerate(all_market_data.items()):
            # Throttle to every 10 markets to reduce Streamlit re-render overhead
            if idx % 10 == 0:
                status_text.text(f"Analysing markets… ({idx}/{total_markets})")

            if not market_data.empty:
                total, green, success_rate = analyze_market_correlation(
                    market_data, stock_green_days, threshold, direction
                )
                results[market_name] = (total, green, success_rate)
            else:
                results[market_name] = (0, 0, 0.0)

            progress_bar.progress(70 + int((idx + 1) / total_markets * 30))

        status_text.text("Analysis complete!")
        progress_bar.progress(100)
        time.sleep(0.5)
        progress_bar.empty()
        status_text.empty()

        st.success("Analysis Complete!")
        results_df = create_results_dataframe(results)

        st.header(f"Summary Statistics — {direction_symbol} {direction} Mode")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Analysis Period", f"{(end_date - start_date).days} days")
        with col2:
            st.metric("Stock Analyzed", stock_ticker)
        with col3:
            st.metric("Total Signals", int(results_df['Total Signals'].sum()))
        with col4:
            active = results_df[results_df['Total Signals'] > 0]['Success Rate (%)']
            avg    = active.mean()
            st.metric("Avg Success Rate", f"{avg:.1f}%" if not pd.isna(avg) else "N/A")

        st.header("📋 Detailed Results")
        st.dataframe(
            results_df.style.background_gradient(
                subset=['Success Rate (%)'],
                cmap='RdYlGn',
                vmin=0,
                vmax=100,
            ).format({
                'Total Signals':    '{:,.0f}',
                'Green Days':       '{:,.0f}',
                'Success Rate (%)': '{:.2f}%',
            }),
            use_container_width=True,
            hide_index=True,
        )

        st.header("Visual Analysis")
        st.plotly_chart(create_bar_chart(results_df), use_container_width=True)

        st.header("Key Insights")

        # FIX: was "> 0" here but "> 30" in the warning — now both use MIN_SIGNALS
        significant = results_df[results_df['Total Signals'] >= MIN_SIGNALS]
        best        = significant.nlargest(1, 'Success Rate (%)')

        if not best.empty:
            row = best.iloc[0]
            st.info(f"""
            **Best Performing Market**: {row['Market']}
            - Success Rate: {row['Success Rate (%)']:.2f}%
            - Total Signals: {row['Total Signals']:.0f}
            - Green Days: {row['Green Days']:.0f}
            """)

        st.warning(f"""
        **Note on Statistical Significance**: Markets with fewer than {MIN_SIGNALS} signals
        may not provide statistically significant results. Consider increasing your date
        range or lowering the threshold for more robust analysis.
        """)

    else:
        st.info("Configure your parameters in the sidebar and click **Run Analysis** to begin!")
        st.markdown("How to Use This Tool")
        st.markdown(f"""
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

        > Markets with fewer than **{MIN_SIGNALS} signals** are excluded from Key Insights.
        """)

# ENTRY POINT

if __name__ == "__main__":
    main()
