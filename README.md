# Quant projects: Python implementations of four Excel workbooks

Python reimplementation of `acp.xlsm`, `risk_budgeting_solution.xlsm`,
`vol_target_solution.xlsx` and `trend_following.xlsx`. Each module is standalone,
reproduces the workbook numerically, and prints a validation block comparing its
output against the cached Excel values.

The four workbooks share a 10-asset cross-asset universe (US and German 10Y
bonds, S&P 500, EuroStoxx 50, Nikkei, MSCI EM, CRB commodities, Iboxx HY US and
EUR, EM debt), daily data from 1998-12-31 to 2014-03-21.

## Layout

```
common/metrics.py                        Excel-compatible performance metrics (ddof=1, 260d year)
common/data.py                           loaders and validation helper
data/                                    data extracted from the workbooks + excel_reference.json
pca/pca_deflation.py                     project 1
risk_budgeting/risk_budgeting.py         project 2
vol_target/vol_target.py                 project 3
trend_following/trend_following.py       project 4
run_all.py                               runs the four modules
```

## Running

```bash
pip install -r requirements.txt
python run_all.py                            # everything
python -m pca.pca_deflation                  # one project
```

## Project 1: PCA by deflation

The workbook maximises the Rayleigh quotient with Solver, then removes each
factor by Hotelling deflation:

$$\max_{\|v\|_2=1} v^\top \Sigma v, \qquad \lambda_k = v_k^\top \Sigma_{k-1} v_k, \qquad \Sigma_k = \Sigma_{k-1} - \lambda_k v_k v_k^\top .$$

Implemented with three solvers: SLSQP on the constrained problem (what Solver
does), power iteration, and `numpy.linalg.eigh` as ground truth. Outputs
eigenvalues, annualised factor volatilities, explained variance, loadings and
asset/factor correlations.

Result on this covariance matrix: PC1 explains 51.3% of total variance (a global
risk-on factor loading on Nikkei, MSCI EM, EuroStoxx), PC2 21.5% (commodities
against equities), PC3 12.0%.

**Finding.** The workbook's third factor is a non-converged Solver point. Its
Rayleigh quotient is $0.01009$ against a true $\lambda_3 = 0.01624$, and the
eigen-residual $\|\Sigma_2 v - \lambda v\|$ is $3.7\times10^{-3}$ versus
$1.4\times10^{-9}$ for PC1. The workbook therefore understates the third factor
at 7.5% of total variance instead of 12.0%. PC1 and PC2 match to $10^{-5}$.

## Project 2: Risk budgeting and ERC

Risk contributions under Euler homogeneity, $\mathrm{RC}_i = w_i (\Sigma w)_i / \sigma(w)$,
$\sum_i \mathrm{RC}_i = \sigma(w)$. A risk-budgeting portfolio solves
$\mathrm{RC}_i(w) = b_i \sigma(w)$ with $w_i > 0$, $\sum_i w_i = 1$.

Solved by the log-barrier formulation, strictly convex and therefore with a
unique solution:

$$y^\star = \arg\min_{y>0} \tfrac{1}{2} y^\top \Sigma y - \sum_i b_i \ln y_i, \qquad w = \frac{y^\star}{\mathbf{1}^\top y^\star}.$$

Three solvers: cyclical coordinate descent (closed form per coordinate, the fast
one in production), damped Newton with backtracking, and SLSQP. All three agree
to $10^{-10}$ and match the workbook to $4\times10^{-7}$; risk contributions match
the budgets to machine precision, against $2.7\times10^{-7}$ for the Solver output.
`equal_risk_contribution()` gives the ERC special case.

Note: the raw budgets in the workbook sum to 1.2 rather than 1. The code
renormalises; the solution is invariant to that rescaling.

## Project 3: Volatility targeting overlay

On the equally-weighted index, with $h = 60$ days and $\sigma^\ast = 5\%$:

$$\hat\sigma_t = \sqrt{260}\,\mathrm{std}(r_{t-h+1},\dots,r_t), \qquad e_t = \frac{\sigma^\ast}{\hat\sigma_t}, \qquad R_t = e_{t-1} r_t + (1 - e_{t-1})\frac{c_{t-1}}{365} .$$

Exposure is applied with a one-day lag and the unfunded fraction is financed at
the cash rate. Replicates the workbook exactly (vol, exposure and NAV paths match
to $10^{-9}$ on every date).

| | equal-weight | vol-targeted |
|---|---|---|
| ann. return (geom) | 7.22% | 5.67% |
| ann. vol | 9.14% | 5.41% |
| Sharpe | 0.81 | 1.05 |
| max drawdown | -34.3% | -16.6% |
| excess kurtosis | 11.5 | 2.7 |

Realised vol lands at 5.41% against a 5% target, the usual gap from a
backward-looking estimator. Exposure averages 0.74 and ranges from 0.14 to 1.48.

Extensions in the module: `max_leverage` cap, RiskMetrics EWMA volatility
estimator, isolated financing leg, turnover series.

## Project 4: Cross-asset trend following

Per-asset 29-day annualised trend and volatility, sized by a single-asset
mean-variance problem:

$$w^\ast_{i,t} = \arg\max_w \; w\mu_{i,t} - \frac{w^2\sigma_{i,t}^2}{2\gamma} = \gamma\frac{\mu_{i,t}}{\sigma_{i,t}^2} = \frac{\gamma}{\sigma_{i,t}}\mathrm{SR}_{i,t}, \qquad \gamma = 0.01 .$$

Adding a quadratic turnover penalty gives an exponential smoothing of the target
position:

$$w_{i,t} = \arg\max_w \; w\mu_{i,t} - \frac{w^2\sigma_{i,t}^2}{2\gamma} - \frac{(w - w_{i,t-1})^2}{2\lambda} \;\Longrightarrow\; w_{i,t} = \nu_{i,t} w^\ast_{i,t} + (1-\nu_{i,t}) w_{i,t-1}, \quad \nu_{i,t} = \frac{\sigma_{i,t}^2}{\sigma_{i,t}^2 + \gamma/\lambda} .$$

The workbook fixes $\nu = 0.1$; `smoothing="state_dependent"` implements the
exact $\nu_{i,t}$. P&L is $R_t = \sum_i w_{i,t-1} r_{i,t}$, positions lagged one
day. Replicates the workbook exactly (Sharpe 2.139, final NAV 965.01, return
series matching to $10^{-12}$).

**Caveats the workbook hides.** Gross exposure is unconstrained: it averages 6.5x
and peaks at 48.9x, because $\gamma/\sigma^2$ blows up on the low-volatility
credit legs. Iboxx HY EUR alone accounts for 51% of P&L with an average weight of
2.34. Neither financing nor transaction costs are charged, and the Sharpe of 2.14
is not achievable at that turnover without them. The module adds a `cost_bps`
option: 2bp of traded notional takes the Sharpe from 2.14 to 2.06 under $\nu=0.1$,
and from 3.10 to 2.86 unsmoothed. A realistic version needs a gross-exposure cap
and a portfolio-level vol target on top.

## Conventions

Both Excel conventions are kept throughout so the replication is exact: sample
standard deviation (`ddof=1`, Excel's `STDEV`/`STDEVA`) and a 260-business-day
year. Cash accrues ACT/365. `common/metrics.py` also reports geometric returns,
drawdowns and Calmar, which the workbooks do not compute.
