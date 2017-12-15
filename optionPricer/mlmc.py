# -*- coding: utf-8 -*-
"""
Created on Wed Nov 15 09:34:45 2017

@author: rayan
"""

import numpy as np
import scipy.stats as ss
from time import time
from matplotlib import pyplot as plt
import multiprocessing as mp

from sklearn.linear_model import Ridge
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline

class MC_simulation():
    def __init__(self,S):
        self.S=S
    def __call__(self,pricer):
        self.S=pricer.S0*np.exp((pricer.rate-0.5*pricer.vol**2)*pricer.maturity+pricer.vol*np.sqrt(pricer.maturity)*np.random.normal(0,1))
        return self.S

class M1LMC_simulation():
    def __init__(self,S):
        self.S=S
    def __call__(self,pricer,n,schema):
        dt=pricer.maturity/n
        W=build_BM(n,np.sqrt(dt))
        if schema=="euler":
            self.S=self.S0
            for j in range(n):
                self.S=pricer.euler(self.S,dt,W[j+1]-W[j])
        elif schema=="milstein":
            self.S=self.S0
            for j in range(n):
                self.S=pricer.milstein(self.S,dt,W[j+1]-W[j])
        return self.S

def build_BM(n,sig):
    W=np.zeros(n+1)
    for k in range(n):
        W[k+1]=W[k]+np.random.normal(0,sig)
    return W

class optionPricer():
    def __init__(self,S0,K,sigma,T,r=0.05,order="call"):
        self.order=order
        self.S0=S0
        self.strike=K
        self.rate=r
        self.vol=sigma
        self.maturity=T
    def BlackScholes(self):
        d1=(np.log(self.S0/self.strike)+(self.rate+(self.vol**2)/2)*self.maturity)/(self.vol*np.sqrt(self.maturity))
        d2=d1-self.vol*np.sqrt(self.maturity)
        if self.order=="call":
            return (self.S0*ss.norm.cdf(d1)-self.strike*np.exp(-self.rate*self.maturity)*ss.norm.cdf(d2))
        if self.order=="put":
           return self.strike*np.exp(-self.rate*self.maturity)*ss.norm.cdf(-d2(self.S0,self.strike,self.rate,self.vol,self.maturity))-self.S0*ss.norm.cdf(-d1(self.S0,self.strike,self.rate,self.vol,self.maturity))
    def euler(self,S,dt,W):
        return S*(1+self.rate*dt+self.vol*W)
    def milstein(self,S,dt,W):
        return S*(1+self.rate*dt+self.vol*W+0.5*(self.vol**2)*(W**2-dt))
    def mc(self,N,pool):
        # on garde les possibilités de paralléliser ou non pour les comparer
        if pool==None:
            S=[]
            W=np.random.normal(0,1,N)
            for _ in range(N):
                S.append(self.S0*np.exp((self.rate-0.5*self.vol**2)*self.maturity+self.vol*np.sqrt(self.maturity)*W[_]))
        else:
            future_res=[pool.apply_async(MC_simulation(0),(self,)) for _ in range(N)]
            S=[f.get() for f in future_res]
        return S
    def m1lmc(self,N,n,pool=None,schema="euler"):
        s=self.S0
        if pool==None:
            S=np.ones(N)*s
            dt=self.maturity/n
            for j in range(N):
                W=build_BM(n,np.sqrt(dt))
                if schema=="euler":
                    S[j]=self.S0
                    for k in range(n):
                        S[j]=self.euler(S[j],dt,W[k+1]-W[k])
                elif schema=="milstein":
                    S[j]=self.S0
                    for k in range(n):
                        S[j]=self.milstein(S[j],dt,W[k+1]-W[k])
        else:
            future_res=[pool.apply_async(M1LMC_simulation(s),(self,n,schema)) for _ in range(N)]
            S=[f.get() for f in future_res]
        return S
    def mlmc(self,n,m=7,schema="euler"):
        L=int(np.log(n)/np.log(m))
        S=np.zeros(L)
        # l=0
        Payoff=0
        N0=int((m-1)*self.maturity*(n**2)*np.log(n)/np.log(m))
        if self.order=="call":
            for _ in range(N0):
                Payoff+=max(self.S0*(1+self.rate*self.maturity+self.vol*np.random.normal(0,np.sqrt(self.maturity)))-self.strike,0)
        elif self.order=="put":
            for _ in range(N0):
                Payoff+=max(self.strike-self.S0*(1+self.rate*self.maturity+self.vol*np.random.normal(0,np.sqrt(self.maturity))),0)
        Payoff/=N0
        # for l>1
        # inverser le role de n et L, c est n qui donne L
        for l in range(1,L):
            #choix de Nl
            # déterminons la variance de Pl-Pl-1 puis choix de Nl
            Nl=int(N0/(m**l))
            P_thin=np.zeros(Nl)
            P_coarse=np.zeros(Nl)

            for j in range(Nl):
                # on génère les deux mouvements browniens
                dt_thin=self.maturity/(m**l)
                W_thin=build_BM(m**l,np.sqrt(dt_thin))
                S_thin=self.S0
                S_coarse=self.S0
                dt_coarse=self.maturity/(m**(l-1))
                if schema=="euler":
                    for i in range(m**l):
                        S_thin=self.euler(S_thin,dt_thin,W_thin[i+1]-W_thin[i])
                    for i in range(m**(l-1)):
                        S_coarse=self.euler(S_coarse,dt_coarse,W_thin[(i+1)*m]-W_thin[i*m])
                elif schema=="milstein":
                    for i in range(m**l):
                        S_thin=self.milstein(S_thin,dt_thin,W_thin[i+1]-W_thin[i])
                    for i in range(m**(l-1)):
                        S_coarse=self.milstein(S_coarse,dt_coarse,W_thin[(i+1)*m]-W_thin[i*m])
                if self.order=="call":
                    P_thin[j]=max(S_thin-self.strike,0)
                    P_coarse[j]=max(S_coarse-self.strike,0)
                elif self.order=="put":
                    P_thin[j]=max(self.strike-S_thin,0)
                    P_coarse[j]=max(self.strike-S_coarse,0)
            Payoff+= (P_thin-P_coarse).mean()
        return np.exp(-self.rate*self.maturity)*Payoff
    def price(self,method="mc",pool=None,m=7,N=10**4,n=10**2,alpha=0.05,schema="euler"):
        CI=[]
        if method!='mlmc':
            if method=="bs":
                return self.BlackScholes()
            elif method=="mc":    
                start=time()
                S=self.mc(N,pool)
            elif method=="m1lmc":
                start=time()
                S=self.m1lmc(N,n,pool)
            if self.order=="call":
                payoffs=list(map(lambda x:np.exp(-self.rate*self.maturity)*max(x-self.strike,0),S))
                payoff=np.mean(payoffs)
                CI=self.confidence_interval(alpha,payoffs)
            elif self.order=="put":
                payoffs=list(map(lambda x:np.exp(-self.rate*self.maturity)*max(x-self.strike,0),S))
                payoff=np.mean(payoffs)
                CI=self.confidence_interval(alpha,payoffs)
            else:
                raise ValueError("'order' muste be either 'call' or 'put'")      
            end=time()
            return (payoff,end-start,CI)
        elif method=="mlmc":
            start=time()
            payoff=self.mlmc(n,m,schema)
            end=time()
            return (payoff,end-start,CI)

    def confidence_interval(self,alpha,payoff):
        n=len(payoff)
        V=np.std(payoff)**2
        mu=np.mean(payoff)
        if self.order=="call":
            return [mu-ss.norm.cdf(1-alpha/2)*np.sqrt(V/n),
                    mu+ss.norm.cdf(1-alpha/2)*np.sqrt(V/n)]
        elif self.order=="put":
            return [mu-ss.norm.cdf(1-alpha/2)*np.sqrt(V/n),
                    mu+ss.norm.cdf(1-alpha/2)*np.sqrt(V/n)]