from __future__ import division
import numpy as np
import pandas as pd
from pymer4.models import Lm, Lmer
from pymer4.simulate import simulate_lm, simulate_lmm

def test_simulate_lm():

    # Simulate some data
    num_obs = 500
    num_coef = 3
    coef_vals = [10,2.2,-4.1,3]
    mus = [10., 3., 2.]
    corrs = .1
    data, b = simulate_lm(num_obs,
                          num_coef,
                          coef_vals,
                          mus = mus,
                          corrs = corrs)

    # Check predictors are correlated
    # True - Generated < .1
    corr = data.iloc[:,1:].corr().values
    corr = corr[np.triu_indices(corr.shape[0],k=1)]
    assert (np.abs(corrs - corrs) < .1).all()

    # Check column means are correct
    # True - Generated < .1
    means = data.iloc[:,1:].mean(axis=0)
    assert np.allclose(means,mus,atol=.1)

    # Check coefficients are as specified
    assert np.allclose(b,coef_vals)

    # Model simulated data
    m = Lm('DV ~ IV1+IV2+IV3',data=data)
    m.fit(summarize=False)

    # Check parameter recovery
    # True - Recovered < .15 for params and < 1 for intercept
    assert (np.abs(m.coefs.iloc[1:,0] - coef_vals[1:]) < .15).all()
    assert (np.abs(m.coefs.iloc[0,0] - coef_vals[0]) < 1).all()

def test_simulate_lmm():

    # Simulate some data
    num_obs = 50
    num_coef = 3
    num_grps = 100
    mus = [10., 30., 2.]
    coef_vals = [4.,1.8,-2,10]
    corrs = .15
    data, blups, b = simulate_lmm(num_obs,
                          num_coef,
                          num_grps,
                          coef_vals = coef_vals,
                          mus = mus,
                          corrs = corrs)

    # Check data shape (add 2 for DV and group columns)
    assert data.shape == (num_obs*num_grps, num_coef+2)

    # Check group shapes
    group_data = data.groupby("Group")
    assert group_data.ngroups == num_grps
    assert (group_data.apply(lambda grp: grp.shape == (num_obs,num_coef+2))).all()

    # Check coefficients are as specified
    assert np.allclose(b,coef_vals)

    # Check blups are close to population values
    # True - Generated < .25
    np.allclose(coef_vals,blups.mean(axis=0),atol=.25)

    # Check column means within groups
    # True - Generate < .5
    assert (group_data.apply(lambda grp: np.allclose(grp.iloc[:,1:-1].mean(axis=0),mus,atol=.5))).all()

    # Check correlations within group
    # True - Generated < .45
    def grp_corr(grp):
        corr = grp.iloc[:,1:-1].corr().values
        corr = corr[np.triu_indices(corr.shape[0],k=1)]
        return corr

    assert (group_data.apply(lambda grp: (np.abs(grp_corr(grp) - corrs) < .45).all())).all()

    # Model simulated data
    m = Lmer('DV ~ IV1+IV2+IV3 + (IV1+IV2+IV3|Group)',data=data)
    m.fit(summarize=False)

    # Check random effects variance
    # True - Generated < .15
    assert np.allclose(m.ranef_var.iloc[1:-1,-1],corrs,atol=.15)

    # Check parameter recovery
    # True - Recovered < .15 for params and < 1 for intercept
    assert (np.abs(m.coefs.iloc[1:,0] - b[1:]) < .15).all()
    assert (np.abs(m.coefs.iloc[0,0] - b[0]) < 1).all()

    # Check BLUP recovery
    # mean(True - Generated) < .25 (sigma)
    assert np.abs((m.fixef.values - blups.values).ravel()).mean() < .3
