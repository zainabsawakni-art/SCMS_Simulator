# Quick Start Guide

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. **Start the server:**
   ```bash
   python app.py
   ```
   Or use the quick start script:
   ```bash
   python run.py
   ```

2. **Open your browser:**
   Navigate to `http://localhost:5000`

## Basic Usage

1. **Configure Parameters:**
   - Adjust simulation parameters in the control panel
   - Key parameters:
     - **World Size**: Number of customers (start with 100-400 for faster runs)
     - **Insolvency Risk**: Probability of default (3% is typical)
     - **Compensation Ratio**: How much of deficits are covered (70% default)
     - **Incentive System**: Enable/disable rating system

2. **Initialize Simulation:**
   - Click "Setup" to initialize with your parameters

3. **Run Simulation:**
   - **Step**: Run one month at a time
   - **Run 10 Steps**: Execute 10 months quickly
   - **Run 50 Steps**: Execute 50 months (for longer simulations)

4. **Monitor Results:**
   - View metrics in the dashboard cards
   - Check customer distribution chart
   - Monitor fund and debt trends
   - Visualize customer grid

## Understanding the Output

### Metrics Dashboard
- **Month**: Current simulation month
- **Active Customers**: Customers still in the system
- **Bank Assets**: Total bank cash + receivables
- **Fund Net Assets**: Fund assets after reserves and compensation
- **Total Deficit**: Unpaid installments this month
- **Total Compensation**: Amount paid to bank from fund

### Customer Ratings
- **A-rated**: Payment day 1-10 (on time)
- **B-rated**: Payment day 11-19 (moderate delay)
- **C-rated**: Payment day 20+ (late payment)
- **Expelled**: More than 3 late payments

### Visual Grid
- **Green**: Active, A-rated customers
- **Orange**: B-rated customers
- **Red**: C-rated or insolvent customers
- **Gray**: Expelled customers

## Tips

- Start with smaller world sizes (100-400) for faster testing
- Use "Run 10 Steps" for quick experiments
- Monitor fund net assets - if it goes negative, the fund is insolvent
- Watch the zero-risk-period metric to see when non-performing debt clears
- Adjust compensation ratio to see impact on fund sustainability

## Troubleshooting

**Server won't start:**
- Check if port 5000 is already in use
- Ensure all dependencies are installed: `pip install -r requirements.txt`

**Simulation runs slowly:**
- Reduce world_size parameter
- Limit the number of steps in batch runs

**Charts not updating:**
- Refresh the page and re-initialize simulation
- Check browser console for JavaScript errors

