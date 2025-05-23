import argparse, sys, functools
from pathlib import Path
import pandas as pd

def estoque_dp(demanda, min_level, eoq, c_order, c_hold):
    """
    Calcula custo mínimo e política de pedido para um SKU.
    demanda  : lista de consumo por dia   [d0, d1, … dT]
    min_level: ponto de ressuprimento
    eoq      : tamanho fixo do lote a ser comprado
    c_order  : custo fixo por pedido
    c_hold   : custo (%) anual de manter 1 unid/ano   (aprox → dia = /365)
    Retorna: (custo_total, pedidos: list[ (dia, qtd) ])
    """
    T = len(demanda)
    c_hold_day = c_hold / 365.0

    @functools.lru_cache(maxsize=None)
    def f(day, stock):
        if day == T:
            return 0.0                     # nenhum custo depois do horizonte
        # opção 1: não pedir hoje
        stock_after = stock - demanda[day]
        cost_hold = max(stock_after, 0) * c_hold_day
        if stock_after < 0:                # ruptura geraria custo proibitivo
            cost_no_order = float('inf')
        else:
            cost_no_order = cost_hold + f(day + 1, stock_after)
        # opção 2: pedir um lote e receber imediatamente
        stock_new = stock + eoq - demanda[day]
        cost_order = c_order + cost_hold + f(day + 1, stock_new)
        # escolher melhor
        if cost_no_order <= cost_order:
            return cost_no_order
        return cost_order