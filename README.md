### Hi there 👋, I am Jean Philippe Cedric N'DRI. Welcome to my GitHub!

I am a quantitative analyst and data scientist working on systematic trading strategies, portfolio management and factor investing. Previously, I worked as a Quant Analyst at LBP AM, a Quant Researcher in QIS at SG CIB and a Data Scientist at BPCE. My current research focuses on option pricing and agentic AI applied to quantitative research.

<div align="center">

<table>
  <tr>
    <td valign="top"><img src="./ascii.svg" width="370" alt="ASCII art" /></td>
    <td valign="top"><img src="./info-card.svg" width="490" alt="neofetch card" /></td>
  </tr>
</table>

</div>

### Projects

<table>
  <tr>
    <td valign="top" colspan="2">
      <a href="https://github.com/jeanphilippecedricndri-sudo/quantlib-pricing"><b>quantlib-pricing</b></a><br>
      <sub>Python · NumPy · SciPy · pandas · CI</sub><br><br>
      Option pricing library written from scratch, covering the valuation chain of an equity derivatives desk. Workflow: <b>option chain</b> (forward from put-call parity) → <b>implied vol</b> (safeguarded Newton, Brent fallback) → <b>SVI / SSVI surface</b> (butterfly and calendar arbitrage checks) → <b>Dupire local vol</b> → <b>PDE engine</b> (Crank-Nicolson, Rannacher, PSOR: European, American, Bermudan) and <b>Monte Carlo engine</b> (Asians, barriers, lookbacks). Validated against closed forms and a binomial tree: American put 6.0879 vs 6.0904. 44 tests, four executed notebooks, known limits documented.
    </td>
  </tr>
  <tr>
    <td valign="top" width="50%">
      <a href="https://github.com/jeanphilippecedricndri-sudo/multiasset-strat"><b>multiasset-strat</b></a><br>
      <sub>Python · portopt · NumPy · pandas</sub><br><br>
      Systematic multi-asset strategy across stocks, ETFs, bonds and commodities. Workflow: <b>universe</b> (132 proxies) → <b>signals</b> (13 price alphas, z-scored per sleeve) → <b>selection</b> (top 10 lines, hysteresis, trend filter) → <b>allocation</b> (risk parity on sleeve budgets, Ledoit-Wolf) → <b>turnover rules</b> → <b>orders</b>. Walk-forward backtest 2009 to 2026, net of costs: CAGR 15.6% and Sharpe 1.23, against 9.9% and 0.96 for a 60/40. Known limits documented, including survivorship bias. Paper included.
    </td>
    <td valign="top" width="50%">
      <a href="https://github.com/jeanphilippecedricndri-sudo/regime-detection"><b>regime-detection</b></a><br>
      <sub>Python · scikit-learn · XGBoost · LightGBM</sub><br><br>
      Fully causal Bull/Bear regime detection on the S&amp;P 500. Workflow: <b>data</b> → <b>labels</b> (K-Means fitted on train only) → <b>features</b> (15 causal price features) → <b>models</b> (logistic regression, random forest, XGBoost, LightGBM, embargoed CV) → <b>ensemble</b> (soft and hard vote) → <b>backtest</b> (long-only, execution lag, costs). Out of sample: macro-F1 0.942, max drawdown cut from −18.8% to −8.4% at a similar Sharpe. Benchmarked against a naive persistence rule. Paper included.
    </td>
  </tr>
  <tr>
    <td valign="top" width="50%">
      <a href="https://github.com/jeanphilippecedricndri-sudo/portfolio-opt"><b>portfolio-opt</b></a><br>
      <sub>Python · NumPy · SciPy · pandas</sub><br><br>
      Portfolio allocation research toolkit. Risk-based estimators (1/N, inverse volatility, risk parity, ERC, HRP) with sample, Ledoit-Wolf and EWMA covariances, a walk-forward backtester net of transaction costs, and performance and risk metrics (Sharpe, Sortino, CVaR, PSR). Tested, with a full methodology including proofs.
    </td>
    <td valign="top" width="50%">
      <a href="https://github.com/jeanphilippecedricndri-sudo/SystematicOptionStrat"><b>SystematicOptionStrat</b></a><br>
      <sub>Python · pandas · options · volatility</sub><br><br>
      Backtests of systematic option strategies on SPY (2020 to 2022): buy-write, protective put, collar, long straddle, and variance risk premium harvesting through a short straddle and a synthetic variance swap. Includes a synthetic option chain generator so it runs offline.
    </td>
  </tr>
</table>

<div align="center">

<br>

<img src="./contrib-heatmap.svg" width="860" alt="Contribution heatmap" />

</div>
