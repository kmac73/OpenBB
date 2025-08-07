# CFD Trade Mechanics: Long vs. Short

This document explains the mechanics and formulas used in the CFD Profit/Loss calculator for both long (buying) and short (selling) trades.

## The Long Trade (Buying) 📈

A **long trade** is initiated with the expectation that the price of an asset will **rise**. You buy the CFD at one price and aim to sell it later at a higher price to make a profit.

### Risk & Position Sizing

- **Account Balance ($)**
  - **Description:** The total amount of money in your trading account. This is a manual input.
  - **Formula:** `N/A (Manual Input)`
- **Account Risk per Trade (%)**
  - **Description:** The maximum percentage of your account balance you are willing to lose on this single trade. This is a manual input.
  - **Formula:** `N/A (Manual Input)`
- **Initial Stop-Loss Price ($)**
  - **Description:** The price level **below** your entry where the trade will be automatically closed to prevent further losses. This is a manual input.
  - **Formula:** `N/A (Manual Input)`
- **Risk per Trade ($)**
  - **Description:** The total dollar amount you are risking on this trade.
  - **Formula:** `= (Account Balance) * (Account Risk per Trade %)`
- **Risk per Contract ($)**
  - **Description:** The potential loss for a single CFD contract if the price hits your stop-loss.
  - **Formula:** `= (Opening Price) - (Initial Stop-Loss Price)`
- **Position Size (Number of CFDs)**
  - **Description:** The number of CFD contracts to buy to align with your desired risk amount.
  - **Formula:** `= (Risk per Trade $) / (Risk per Contract $)`

### Trade Setup

- **Opening Price ($)**
  - **Description:** The price at which you enter the long trade (buy the CFDs). This is a manual input.
  - **Formula:** `N/A (Manual Input)`
- **Margin Rate (%)**
  - **Description:** The percentage of the total position value that you must put up as collateral (margin). This is set by your broker. This is a manual input.
  - **Formula:** `N/A (Manual Input)`
- **Leverage Ratio**
  - **Description:** Shows how much your trading capital is amplified. For example, a 5% margin rate equals 20:1 leverage.
  - **Formula:** `= 1 / (Margin Rate %)`
- **Notional Position Value ($)**
  - **Description:** The total value of the position you are controlling with leverage.
  - **Formula:** `= (Position Size) * (Opening Price)`
- **Margin Required ($)**
  - **Description:** The amount of your own money required to open and maintain the trade. This is your "good-faith deposit."
  - **Formula:** `= (Notional Position Value) * (Margin Rate %)`

### Scenario Analysis

- **Current Market Price ($)**
  - **Description:** The live, real-time price of the asset. This is a manual input for scenario testing.
  - **Formula:** `N/A (Manual Input)`
- **Highest/Lowest Price Reached ($)**
  - **Description:** For a long trade, this is the **highest** price the asset has reached since you opened the position. This is used for the trailing stop calculation. This is a manual input.
  - **Formula:** `N/A (Manual Input)`
- **Risk/Reward Ratio**
  - **Description:** Defines your desired profit relative to your risk. A ratio of 2 means you are aiming for a profit twice the size of your potential loss. This is a manual input.
  - **Formula:** `N/A (Manual Input)`
- **Profit Target Price ($)**
  - **Description:** The price level **above** your entry where you plan to take profit.
  - **Formula:** `= (Opening Price) + ((Risk per Contract $) * (Risk/Reward Ratio))`
- **Trailing Stop Percentage (%)**
  - **Description:** The percentage below the highest price reached at which to set a dynamic stop-loss. This is a manual input.
  - **Formula:** `N/A (Manual Input)`
- **Active Trailing Stop Price ($)**
  - **Description:** A dynamic stop-loss that moves up as the price rises, locking in profits. It only becomes active once the price is above your entry.
  - **Formula:** `=IF((Highest Price Reached) > (Opening Price), (Highest Price Reached) * (1 - Trailing Stop %), "")`
- **Final Exit Price ($)**
  - **Description:** Determines the outcome of the trade by checking if the profit target or a stop-loss has been hit. If not, it shows the current price.
  - **Formula:** `=IF((Current Market Price) >= (Profit Target Price), (Profit Target Price), IF(AND((Active Trailing Stop) <> "", (Current Market Price) <= (Active Trailing Stop)), (Active Trailing Stop), (Current Market Price)))`

### Final Results

- **Gross Profit / Loss ($)**
  - **Description:** The total profit or loss from the trade before deducting any costs.
  - **Formula:** `= ((Final Exit Price) - (Opening Price)) * (Position Size)`
- **Round Trip Transaction Cost**
  - **Description:** The broker's fee for both opening and closing the trade. This is a manual input representing the cost per contract.
  - **Formula:** `N/A (Manual Input)`
- **Net Profit**
  - **Description:** The final profit or loss after all transaction costs have been deducted.
  - **Formula:** `= (Gross Profit / Loss) - ((Round Trip Transaction Cost) * (Position Size))`
- **Return on Margin (%)**
  - **Description:** The net profit or loss expressed as a percentage of the margin you used to open the trade.
  - **Formula:** `= (Net Profit) / (Margin Required)`

## The Short Trade (Selling) 📉

A **short trade** is initiated with the expectation that the price of an asset will **fall**. You borrow and sell a CFD at one price, aiming to buy it back later at a lower price to make a profit.

### Risk & Position Sizing

- **Account Balance ($)**: Same as long trade.
- **Account Risk per Trade (%)**: Same as long trade.
- **Initial Stop-Loss Price ($)**
  - **Description:** The price level **above** your entry where the trade will be automatically closed to prevent further losses.
  - **Formula:** `N/A (Manual Input)`
- **Risk per Trade ($)**: Same as long trade.
- **Risk per Contract ($)**
  - **Description:** The potential loss for a single CFD contract if the price hits your stop-loss.
  - **Formula:** `= (Initial Stop-Loss Price) - (Opening Price)`
- **Position Size (Number of CFDs)**: Same as long trade.

### Trade Setup

- **Opening Price ($)**
  - **Description:** The price at which you enter the short trade (sell the CFDs).
  - **Formula:** `N/A (Manual Input)`
- **Margin Rate (%)**: Same as long trade.
- **Leverage Ratio**: Same as long trade.
- **Notional Position Value ($)**: Same as long trade.
- **Margin Required ($)**: Same as long trade.

### Scenario Analysis

- **Current Market Price ($)**: Same as long trade.
- **Highest/Lowest Price Reached ($)**
  - **Description:** For a short trade, this is the **lowest** price the asset has reached since you opened the position.
  - **Formula:** `N/A (Manual Input)`
- **Risk/Reward Ratio**: Same as long trade.
- **Profit Target Price ($)**
  - **Description:** The price level **below** your entry where you plan to take profit.
  - **Formula:** `= (Opening Price) - ((Risk per Contract $) * (Risk/Reward Ratio))`
- **Trailing Stop Percentage (%)**: Same as long trade.
- **Active Trailing Stop Price ($)**
  - **Description:** A dynamic stop-loss that moves down as the price falls. It is placed above the lowest price reached.
  - **Formula:** `=IF((Lowest Price Reached) < (Opening Price), (Lowest Price Reached) * (1 + Trailing Stop %), "")`
- **Final Exit Price ($)**
  - **Description:** Determines the outcome by checking if the price has dropped to the profit target or risen to a stop-loss.
  - **Formula:** `=IF((Current Market Price) <= (Profit Target Price), (Profit Target Price), IF(AND((Active Trailing Stop) <> "", (Current Market Price) >= (Active Trailing Stop)), (Active Trailing Stop), (Current Market Price)))`

### Final Results

- **Gross Profit / Loss ($)**
  - **Description:** The total profit or loss from the trade before deducting any costs.
  - **Formula:** `= ((Opening Price) - (Final Exit Price)) * (Position Size)`
- **Round Trip Transaction Cost**: Same as long trade.
- **Net Profit**: Same as long trade.
- **Return on Margin (%)**: Same as long trade.