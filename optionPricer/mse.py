from mlmc import optionPricer
from calibrate_py import dikotomy,loc_search,simulated_annealing
import multiprocessing as mp
import matplotlib.pyplot as plt
import numpy as np


o=optionPricer(100,100,0.25,1,r=0.05)

########### Calcul de l'erreur d'une méthode par rapport à la réference (formule de Black-Scholes) ###########

## tentative de paralléliser le calcul de MSE 

# class MSE_computation():
#     def __init__(self):
#         self.err=0
#         self.times=[]
#     def __call__(self,ref,pricer,simulations,method):
#         omc,t=pricer.price(method,N=simulations)
#         self.err+=(omc-ref)**2
#         self.times.append(t)
#         return self.err,self.times

# def mse(ref,pricer,simulations,method="mc",max_iter=100):
#     pool=mp.Pool(4)
#     future_res=[pool.apply_async(MSE_computation(),(ref,pricer,simulations,method)) for _ in range(max_iter)]
#     data=[f.get() for f in future_res]
#     err=np.sum([data[k][0] for k in range(len(data))])
#     times=[data[k][1] for k in range(len(data))]
#     return err/max_iter,np.mean(times)

def mse(ref,pricer,n,N,method,pool=None,max_iter=300):
    err=0
    times=[]
    for _ in range(max_iter):
        print(method+' {}% '.format(100*_/max_iter))
        output=pricer.price(method,pool,N=N,n=n)
        omc,t=output[0],output[1]
        err+=(omc-ref)**2
        times.append(t)
    return err/max_iter,np.mean(times)

obs=o.price(method="bs")
a=np.array([20,30,50,60,70,80])

########## Comparison of MLMC and MC ###############

pool=mp.Pool(4)
#a_SA=list(map(lambda x: simulated_annealing(x,polynom),a))
#a_locsearch=list(map(lambda x: loc_search(x,1e-3,4,10),a))
a_diko=list(map(lambda x: loc_search(x,1e-2,7,10,2,3500),a))
outputs_m1lmc=list(map(lambda x,y: mse(obs,o,x,y,"m1lmc"),a,a_diko))
MSE_m1lmc=[outputs_m1lmc[k][0] for k in range(len(outputs_m1lmc))]
TIMES_m1lmc=[outputs_m1lmc[k][1] for k in range(len(outputs_m1lmc))]

outputs_mlmc=list(map(lambda x: mse(obs,o,x,0,"mlmc"),a))
MSE_mlmc=[outputs_mlmc[k][0] for k in range(len(outputs_mlmc))]
TIMES_mlmc=[outputs_mlmc[k][1] for k in range(len(outputs_mlmc))]

plt.plot(np.log10(TIMES_m1lmc),np.log10(MSE_m1lmc),marker='s',label="EE")
plt.plot(np.log10(TIMES_mlmc),np.log10(MSE_mlmc),marker="o",label="MLMC")
plt.grid(True)
plt.xlabel("log of the computation time")
plt.ylabel("log of the MSE")
plt.legend(loc=1)
plt.show()

###### to show the benefits of parallelization #########
# outputs_m1lmc_unthreaded=list(map(lambda x: mse(obs,o,x,None,"m1lmc"),a))
# MSE_m1lmc_unthreaded=[outputs_m1lmc_unthreaded[k][0] for k in range(len(outputs_m1lmc_unthreaded))]
# TIMES_m1lmc_unthreaded=[outputs_m1lmc_unthreaded[k][1] for k in range(len(outputs_m1lmc_unthreaded))]

# plt.plot(np.log10(a),np.log10(TIMES_m1lmc),marker='o',label="With parallelization")
# plt.plot(np.log10(a),np.log10(TIMES_m1lmc_unthreaded),marker='<',color='r',label="No parallelization")
# plt.xlabel("$log_{10}$ of the number of samples for MC simulations \n with Euler schematization")
# plt.ylabel("$log_{10}$ of the computation time")
# plt.legend(loc=2)
# plt.tight_layout()
# plt.show()