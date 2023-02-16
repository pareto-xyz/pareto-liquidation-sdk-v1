# Pareto Order Book Liquidation SDK V1

**[Disclaimer: This repository is no longer maintained and is meant for primarily educational purposes.]**

Part of the series detailed in this [whitepaper](https://github.com/pareto-xyz/pareto-order-book-whitepaper/blob/main/how_to_orderbook.pdf). 

If accounts on Pareto's exchange fall under margin, then they are at risk of being liquidated. The liquidation is decentralized such that any account can claim the liquidated position(s) from the user. Liquidators are provided a reward per position liquidated. 

This repo contains a Python SDK with scripts to find accounts below margin and to perform liquidations. Please note that liquidations are not a risk-free endeavor. Proceed at your own risk.

## Setup

Install the package locally:

`pip install -e ./`
