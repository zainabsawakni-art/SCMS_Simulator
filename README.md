# Credit Insurance and Rating System Simulation

A Python web application that replicates the NetLogo CIES 9.1 model - an integrated credit insurance, rating, and incentive system simulation.

## Overview

This simulation models a credit system with:
- **Customers**: Borrowers arranged in a grid network
- **Bank**: Lending institution providing loans
- **Mutual Insurance Fund**: Collects contributions and pays compensation for defaults
- **Incentive System**: Payment day ratings (A/B/C) based on payment timing
- **Peer Effects**: Customer behavior influenced by neighbors

## Features

### Complete NetLogo Interface Replication

All NetLogo interface elements have been replicated:

#### Sliders
- `world-size`: Number of customers (100-5000)
- `base-rate`: Base fee for fund contribution (0-0.5%)
- `premium-increment`: Additional fee per day delay (0-0.15%)
- `max-day`: First day considered late (5-30)
- `insolvency-risk`: Probability of default (0-25%)
- `unpaid-fraction`: Average unpaid fraction when default occurs (50-100%)
- `min-installment` / `max-installment`: Installment bounds ($0-$10,000)
- `min-periods` / `max-periods`: Loan duration bounds (12-90 months)
- `No-of-periods`: Simulation length when renew-financing is enabled (0-1000)
- `peer-effect`: Peer pressure weighting (0-100%)
- `p-day-response`: Preferred day adherence factor (0.5-1.5)
- `premium-response`: Premium aversion factor (0.5-1.5)
- `randomness`: Random distribution bounds (5-95%)
- `reserve-ratio`: Fund reserve percentage (0-100%)
- `compensation-ratio`: Compensation threshold (0-100%)

#### Switches
- `incentive-system`: Enable/disable rating system
- `adjust-compensation`: Pay accumulated deficits when fund allows
- `fix-random-seed`: Use fixed seed for reproducibility
- `renew-financing`: Renew loans when customers pay off debt

#### Buttons
- `Setup`: Initialize simulation with current parameters
- `Go`: Run one simulation step
- `Stop`: Stop automatic running

#### Monitors (Metrics)
- `month`: Current simulation month
- `No. of customers`: Total number of customers
- `rounds`: Maximum financing rounds
- `expelled-agents`: Customers expelled due to late payments
- `zero-risk period`: Month when non-performing debt reaches zero
- `seed-number`: Random seed used
- `bank-assets`, `bank-cash`, `bank-receivables`: Bank financial metrics (per capita)
- `performing debt`, `non-performing debt`: Debt metrics (per capita)
- `fund total-assets`, `fund net-assets`, `reserves`: Fund metrics (per capita)
- `payment day`, `contribution %`, `max day`: Payment metrics
- `A-rated`, `B-rated`, `C-rated`: Customer rating counts
- `insolvent agents`: Customers experiencing insolvency shock
- `avg points`: Average customer points
- `balance`: Consistency check metric
- `receivables-check`: Bank receivables consistency check

#### Plots
- **Compensations**: Shows mean compensation received, deficit, and additional compensation over time
- **Fund (per capita)**: Shows fund assets, net assets, non-performing loans, and reserves over time
- **Rating**: Bar chart showing current distribution of A/B/C rated customers

#### Visualizations
- **Customer Grid**: Interactive scatter plot showing customer positions colored by rating/status
  - Green: A-rated (payment day 1-10)
  - Orange: B-rated (payment day 11-19)
  - Red: C-rated (payment day 20+) or Insolvent
  - Gray: Expelled customers

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

### Local Development

#### Option 1: Using the run script
```bash
python run.py
```

#### Option 2: Direct Streamlit command
```bash
streamlit run app.py
```

The application will automatically open in your default web browser at `http://localhost:8501`.

### Streamlit Community Cloud Deployment

#### Quick Deploy:
1. **Push to GitHub** (if not already done):
   ```bash
   git add .
   git commit -m "Ready for Streamlit Cloud"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**:
   - Go to: https://share.streamlit.io/
   - Sign in with GitHub
   - Click "New app"
   - Select repository: `zainabsawakni-art/SCMS_Simulator`
   - Set **Main file path**: `app.py`
   - Click "Deploy"

3. **Your app will be live** at: `https://scms-simulator.streamlit.app`

See `STREAMLIT_CLOUD_DEPLOYMENT.md` for detailed instructions.

## Usage

1. **Configure Parameters**: Adjust sliders and switches in the sidebar to set simulation parameters
2. **Initialize**: Click "Setup" to initialize the simulation with your parameters
3. **Run**: Click "Go" to run one step, or enable auto-run for continuous simulation
4. **Monitor**: View metrics, plots, and visualizations in the main panel
5. **Export**: Download simulation state (JSON) or history (CSV) for analysis

## Understanding the Model

### Customer Behavior
- Each customer has a loan with monthly installments
- Customers may experience "insolvency shocks" that prevent full payment
- Payment timing affects their rating (A/B/C) and fund contribution rate
- Customers are influenced by neighbors' payment behavior (peer effect)
- After 3 late payments, customers are expelled from the system

### Fund Operations
- Customers contribute to the mutual insurance fund based on payment timing
- The fund compensates the bank for unpaid deficits
- Compensation is limited by `compensation-ratio` and fund net assets
- Reserves can be set aside via `reserve-ratio`

### Bank Operations
- Bank provides loans and receives repayments
- Receives compensation from fund for defaults
- Tracks performing and non-performing debt

## Project Structure

```
.
├── app.py                  # Main Streamlit application
├── run.py                  # Run script
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── nlogo/                 # Simulation models
    ├── models/
    │   ├── customer.py   # Customer/agent model
    │   ├── bank.py        # Bank model
    │   └── fund.py        # Mutual insurance fund model
    └── simulation/
        └── world.py       # Main simulation world/engine
```

## Technical Details

### Framework Choice: Streamlit
Streamlit was chosen because it:
- Provides native support for sliders, switches, buttons matching NetLogo interface
- Enables real-time interactive visualizations
- Simplifies layout management
- Supports Plotly for advanced charts
- Allows easy data export

### Code Organization
- **Modular Design**: Separate models for Customer, Bank, and Fund
- **World Engine**: Central simulation engine coordinating all entities
- **State Management**: Session state for maintaining simulation state
- **History Tracking**: Records all simulation steps for plotting

### NetLogo Correspondence
Each NetLogo procedure has been mapped to Python methods:
- `setup` → `World.setup()`
- `go` → `World.step()`
- `cal-*` procedures → `calculate_*` methods
- Patch variables → Customer attributes
- Global variables → World attributes

## Data Export

The application supports exporting:
- **Current State (JSON)**: Complete simulation state at current month
- **History (CSV)**: Time series data of all metrics across simulation steps

## Notes

- For faster testing, use smaller `world-size` values (100-400)
- The simulation stops automatically when reaching `max-periods` or `No-of-periods`
- Enable `fix-random-seed` for reproducible experiments
- Monitor `fund net-assets` - negative values indicate fund insolvency

## Credits

Based on the NetLogo CIES 9.1 model by Islamic Research and Training Institute.

## License

© Islamic Research and Training Institute

