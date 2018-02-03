from mlmc import optionPricer
from calibrate_py import dikotomy,loc_search,simulated_annealing
import multiprocessing as mp
import matplotlib.pyplot as plt
import numpy as np

o=optionPricer(100,100,0.2,3,"BS","E","milstein",kappa=3,rho=0,xi=0.2,theta=.9,v0=0.1)

########### Calcul de l'erreur d'une méthode par rapport à la réference (formule de Black-Scholes) ###########

def mse(ref,pricer,n,N,method,pool=None,max_iter=100):
    err=0
    times=[]

    for _ in range(max_iter):
        print(method+' {}% '.format(100*_/max_iter))
        output=pricer.price("call",method,N=N,n=n)
        omc,t=output[0],output[1]
        err+=(omc-ref)**2
        times.append(t)
    return err/max_iter,np.mean(times)

obs,t_ref=o.price("call",method="bs")
#obs=18.501473532023425 #asiat
#obs=62.58904549 #pour le modele de Heston

a=np.array([25,30,35,40])
loga=np.log(a)*a

########## Comparison of MLMC and MC ###############

#pool=mp.Pool(4)
#a_SA=list(map(lambda x: simulated_annealing(x,polynom),a))
#a_locsearch=list(map(lambda x: loc_search(x,1e-3,4,10),a))
#a_ls=list(map(lambda x: loc_search(x,1e-2,7,10,100,4000),a))
#a_ls=[77,664,649,1062,6783,7187]
a_ls_hes=[500,450,700,900]

outputs_mc=list(map(lambda x,y: mse(obs,o,x,y,"mc"),a,a_ls_hes))
MSE_mc=[outputs_mc[k][0] for k in range(len(outputs_mc))]
TIMES_mc=[outputs_mc[k][1] for k in range(len(outputs_mc))]

outputs_mlmc=list(map(lambda x: mse(obs,o,x,0,"mlmc"),a))
MSE_mlmc=[outputs_mlmc[k][0] for k in range(len(outputs_mlmc))]
TIMES_mlmc=[outputs_mlmc[k][1] for k in range(len(outputs_mlmc))]

plt.plot(np.log(TIMES_mc),np.log(MSE_mc),marker='s',label="MC with Milstein scheme")
plt.plot(np.log(TIMES_mlmc),np.log(MSE_mlmc),marker="o",label="MLMC with Milstein scheme")
plt.grid(True)
plt.xlabel("log of computation time")
plt.ylabel("log of MSE")
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