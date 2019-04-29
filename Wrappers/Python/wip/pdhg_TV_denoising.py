#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 22 14:53:03 2019

@author: evangelos
"""

from ccpi.framework import ImageData, ImageGeometry

import numpy as np 
import numpy                          
import matplotlib.pyplot as plt

from ccpi.optimisation.algorithms import PDHG, PDHG_old

from ccpi.optimisation.operators import BlockOperator, Identity, Gradient
from ccpi.optimisation.functions import ZeroFunction, L2NormSquared, \
                      MixedL21Norm, BlockFunction

from skimage.util import random_noise

from timeit import default_timer as timer
#def dt(steps):
#    return steps[-1] - steps[-2]

# Create phantom for TV Gaussian denoising

N = 100

data = np.zeros((N,N))
data[round(N/4):round(3*N/4),round(N/4):round(3*N/4)] = 0.5
data[round(N/8):round(7*N/8),round(3*N/8):round(5*N/8)] = 1

ig = ImageGeometry(voxel_num_x = N, voxel_num_y = N)
ag = ig

# Create noisy data. Add Gaussian noise
n1 = random_noise(data, mode = 'gaussian', mean=0, var = 0.05, seed=10)
noisy_data = ImageData(n1)


plt.imshow(noisy_data.as_array())
plt.title('Noisy data')
plt.show()

# Regularisation Parameter
alpha = 0.5

#method = input("Enter structure of PDHG (0=Composite or 1=NotComposite): ")
method = '1'

if method == '0':

    # Create operators
    op1 = Gradient(ig)
    op2 = Identity(ig, ag)

    # Form Composite Operator
    operator = BlockOperator(op1, op2, shape=(2,1) ) 

    #### Create functions
      
    f1 = alpha * MixedL21Norm()
    f2 = 0.5 * L2NormSquared(b = noisy_data)    
    f = BlockFunction(f1, f2)  
                                      
    g = ZeroFunction()
    
else:
    
    ###########################################################################
    #         No Composite #
    ###########################################################################
    operator = Gradient(ig)
    f =  alpha * MixedL21Norm()
    g =  0.5 * L2NormSquared(b = noisy_data)
        
    
diag_precon =  False

if diag_precon:
    
    def tau_sigma_precond(operator):
        
        tau = 1/operator.sum_abs_row()
        sigma = 1/ operator.sum_abs_col()
               
        return tau, sigma

    tau, sigma = tau_sigma_precond(operator)
             
else:
    # Compute operator Norm
    normK = operator.norm()
    
    # Primal & dual stepsizes
    sigma = 1
    tau = 1/(sigma*normK**2)


opt = {'niter':5000}
opt1 = {'niter':5000, 'memopt': True}

t1 = timer()
res, time, primal, dual, pdgap = PDHG_old(f, g, operator, tau = tau, sigma = sigma, opt = opt) 
t2 = timer()

t3 = timer()
res1, time1, primal1, dual1, pdgap1 = PDHG_old(f, g, operator, tau = tau, sigma = sigma, opt = opt1) 
t4 = timer()

plt.figure(figsize=(15,15))
plt.subplot(3,1,1)
plt.imshow(res.as_array())
plt.title('no memopt')
plt.colorbar()
plt.subplot(3,1,2)
plt.imshow(res1.as_array())
plt.title('memopt')
plt.colorbar()
plt.subplot(3,1,3)
plt.imshow((res1 - res).abs().as_array())
plt.title('diff')
plt.colorbar()
plt.show()
# 
plt.plot(np.linspace(0,N,N), res1.as_array()[int(N/2),:], label = 'memopt')
plt.plot(np.linspace(0,N,N), res.as_array()[int(N/2),:], label = 'no memopt')
plt.legend()
plt.show()
#
print ("Time: No memopt in {}s, \n Time: Memopt in  {}s ".format(t2-t1, t4 -t3))
diff = (res1 - res).abs().as_array().max()
#
print(" Max of abs difference is {}".format(diff))


#%% Check with CVX solution

from ccpi.optimisation.operators import SparseFiniteDiff

try:
    from cvxpy import *
    cvx_not_installable = True
except ImportError:
    cvx_not_installable = False


if cvx_not_installable:

    ##Construct problem    
    u = Variable(ig.shape)
    
    DY = SparseFiniteDiff(ig, direction=0, bnd_cond='Neumann')
    DX = SparseFiniteDiff(ig, direction=1, bnd_cond='Neumann')
    
    # Define Total Variation as a regulariser
    regulariser = alpha * sum(norm(vstack([DX.matrix() * vec(u), DY.matrix() * vec(u)]), 2, axis = 0))
    fidelity = 0.5 * sum_squares(u - noisy_data.as_array())
    
    # choose solver
    if 'MOSEK' in installed_solvers():
        solver = MOSEK
    else:
        solver = SCS  
        
    obj =  Minimize( regulariser +  fidelity)
    prob = Problem(obj)
    result = prob.solve(verbose = True, solver = solver)
    
    diff_cvx = numpy.abs( res.as_array() - u.value )
    
    # Show result
    plt.figure(figsize=(15,15))
    plt.subplot(3,1,1)
    plt.imshow(res.as_array())
    plt.title('PDHG solution')
    plt.colorbar()
    
    plt.subplot(3,1,2)
    plt.imshow(u.value)
    plt.title('CVX solution')
    plt.colorbar()
    
    plt.subplot(3,1,3)
    plt.imshow(diff_cvx)
    plt.title('Difference')
    plt.colorbar()
    plt.show()
    
    plt.plot(np.linspace(0,N,N), res1.as_array()[int(N/2),:], label = 'PDHG')
    plt.plot(np.linspace(0,N,N), u.value[int(N/2),:], label = 'CVX')
    plt.legend()
    

    
    
    print('Primal Objective (CVX) {} '.format(obj.value))
    print('Primal Objective (PDHG) {} '.format(primal[-1]))



