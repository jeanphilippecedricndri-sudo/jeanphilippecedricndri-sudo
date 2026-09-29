### Hi there 👋, I am Jean Philippe Cedric N'DRI. Welcome to my GitHub!

I am a quantitative analyst and data scientist working on systematic
trading strategies, portfolio management and factor investing.
Previously, I worked as a Quant Analyst at LBP AM, a Quant Researcher
in QIS at SG CIB and a Data Scientist at BPCE. My current research
focuses on option pricing and agentic AI applied to quantitative research.

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
      <a href="https://github.com/jeanphilippecedricndri-sudo/regime-detection"><b>regime-detection</b></a><br>
      <sub>Python · scikit-learn · XGBoost · LightGBM</sub><br><br>
      Fully causal Bull/Bear regime detection on the S&amp;P 500.
      Workf<b>data</b> → <b>labels</b> (K-Means fitted on train only)
      → <b>features</b> (15 causal price features)
      → <b>models</b> (logistic regression, random forest, XGBoost,
      LightGBM, embargoed CV) → <b>ensemble</b> (soft and hard vote)
      → <b>backtest</b> (long-only, execution lag, costs).
      Out of sample: macro-F1 0.942, max drawdown cut from −18.8% to at a similar Sharpe. Benchmarked against a naive persistence
      rule. Paper included.
    </td>
  </tr>
  <tr>
    <td valign="top" width="50%">
      <a href="https://github.com/jeanphilippecedricndri-sudo/portfolio-opt"><b>portfolio-opt</b></a><br>
      <sub>Python · NumPy · SciPy · pandas</sub><br><br>
      Portfolio allocation research toolkit. Risk-based estimators
      (1/N, inverse volatility, risk parity, ERC, HRP) with sample,
      Ledoit-Wolf and EWMA covariances, a walk-forward backtester net
      of transaction costs, and performance and risk metrics (Sharpe,
      Sortino, CVaR, PSR). Tested, with a full methodology including proofs.
    </td>
    <td valign="top" width="50%">
      <a href="https://github.com/jeanphilippecedricndri-sudo/SystematicOptionStrat"><b>SystematicOptionStrat</b></a><br>
      <sub>Python · pandas · options · volatility</sub><br><br>
      Backtests of systematic option strategies on SPY (2020 to 2022):
      buy-write, protective put, collar, long stradnd variance risk
      premium harvesting through a short straddle and a synthetic variance
      swap. Includes a synthetic option chain generator so it runs offline.
    </td>
  </tr>
</table>

<div align="center">

<br>

<img src="./contrib-heatmap.svg" width="860" alt="Contribution heatmap" />

</div>
