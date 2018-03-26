import sys
import os
import getopt
import pickle
import pop_quality
from multiprocessing import Pool
from scipy import stats
import scipy.stats as stats
import numpy as np

def get_actual_rank(rank_meme_dic):
        key = 1
        actual_rank_meme_dic = {}
        for i in rank_meme_dic:
            if i == 1:
                actual_rank_meme_dic[i] = rank_meme_dic[i]
            else:
                key += len(rank_meme_dic[i-1])
                actual_rank_meme_dic[key] = rank_meme_dic[i]
        return actual_rank_meme_dic

def compute_kendall_tao(data):
    pop_quality_dic = {}
    quality_list = []
    for fitness in data:
        quality_list.append(fitness)
        count = data[fitness]
        if not pop_quality_dic.has_key(float(count)):
            pop_quality_dic[float(count)] = [float(fitness),]
        else:
            pop_quality_dic[float(count)].append(float(fitness))
    rank_by_pop = {}
    rank_by_quality = {}
    rp = 1
    for pop in sorted(pop_quality_dic.keys(),reverse=True):
        rank_by_pop[rp] = pop_quality_dic[pop]
        rp += 1
    actual_rank_pop = get_actual_rank(rank_by_pop)
    rq = 1
    for quality in sorted(quality_list,reverse=True):
        rank_by_quality[rq] = [quality,]
        rq += 1
    actual_rank_quality = get_actual_rank(rank_by_quality)
    quality_rq = {}
    quality_rp = {}
    for i in actual_rank_pop:
        for j in actual_rank_pop[i]:
            quality_rp[j] = i
    for i in actual_rank_quality:
        for j in actual_rank_quality[i]:
            quality_rq[j] = i
    x_rp = []
    y_rq = []
    for i in quality_rp:
        x_rp.append(quality_rp[i])
        y_rq.append(quality_rq[i])
    tau, p_value = stats.kendalltau(x_rp, y_rq)
    return tau, p_value

def run(params):
    sample_type = 'uniform'
    urn_size = 1000
    total_time = 1000000
    total_run = 41
    alpha = params['alpha']
    beta = params['beta']
    out ='urn_pref/'

    tau_list =[]
    expected_quality = []
    tau_file = open(out+'tau/tau_'+str(total_run)+'_alpha_'+str(alpha)+'_beta_'+str(beta)+'_size_'+str(urn_size/1000)+'k.csv','w')
    quality_file = open(out+'avr_quality/quality_'+str(total_run)+'_alpha_'+str(alpha)+'_beta_'+str(beta)+'_size_'+str(urn_size/1000)+'k.csv','w')
    run_file = open(out+'run/run_'+str(total_run)+'_alpha_'+str(alpha)+'_beta_'+str(beta)+'_size_'+str(urn_size/1000)+'k.csv','w')
    for r in range(total_run):
    	cascade_obj = pop_quality.Cascade()
	if alpha == 10:
	    running_average ,fitness_dic = cascade_obj.sim_prefential_attachemnt(urn_size, total_time,beta, alpha,sample_type)
	else:
            running_average ,fitness_dic = cascade_obj.sim_urn(urn_size, total_time,beta, alpha,sample_type)
	tau , p = compute_kendall_tao(fitness_dic)	
	tau_list.append(tau)
	expected_quality.append(running_average)
	run_file.write(str(r)+','+str(tau)+','+str(p)+','+str(running_average)+'\n')
    q_avr = np.mean(expected_quality)
    q_e = stats.sem(expected_quality)
    q_std = np.std(expected_quality)
    quality_file.write(str(q_avr)+','+str(q_std)+','+str(q_e)+'\n')
    tau_avr = np.mean(tau_list)
    tau_std = np.std(tau_list)
    tau_err =stats.sem(tau_list)
    tau_file.write(str(tau_avr)+','+str(tau_std)+','+str(tau_err)+'\n')

if __name__ == '__main__':
    params_list = []
    for beta in [0.0,0.05,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]:
            for alpha in [0.0,0.5,1.0,2.0]:
                params_list.append({'beta':beta,'alpha':alpha})
    pool = Pool(processes = 16)
    result = pool.map(run,params_list)
    pool.close()
    pool.join() 

