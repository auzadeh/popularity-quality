import pickle
import sys,getopt
import operator
import math
import itertools
import networkx as nx
import numpy as np
import scipy as sp
import random 
from scipy import stats

class Cascade(object):

    def shift_dic_down(self,dic,meme_rank):
        d_keys = dic.keys()
        point = meme_rank#d_keys.index(meme_rank)
        for i in range(d_keys[len(d_keys)-1],point-1,-1):
            dic[i+1] = dic[i]
        return dic

    def update_rank(self,selected_marble,rank_meme_dic,fitness_dic):
        selected_marble_rank = rank_meme_dic.keys()[rank_meme_dic.values().index(filter(lambda x:selected_marble in x,rank_meme_dic.values())[0])]
        rank_meme_dic[selected_marble_rank].remove(selected_marble)
        if not rank_meme_dic.has_key(selected_marble_rank-1):
            if len(rank_meme_dic[selected_marble_rank]) < 1:
                rank_meme_dic[selected_marble_rank] = [selected_marble,]
            else:
                rank_meme_dic = self.shift_dic_down(rank_meme_dic,selected_marble_rank)
            rank_meme_dic[selected_marble_rank] = [selected_marble,]
        else:
            if len(rank_meme_dic[selected_marble_rank]) < 1:
                higher_rank_meme = rank_meme_dic[selected_marble_rank-1][0]
                if fitness_dic[selected_marble] == fitness_dic[higher_rank_meme]:
                    rank_meme_dic[selected_marble_rank-1].append(selected_marble)
                    ### shift up
                    for lr in range(selected_marble_rank+1,rank_meme_dic.keys()[len(rank_meme_dic)-1]+1):
                        rank_meme_dic[lr-1] = rank_meme_dic[lr]
                    del rank_meme_dic[rank_meme_dic.keys()[len(rank_meme_dic)-1]]
                elif fitness_dic[selected_marble] < fitness_dic[higher_rank_meme]:
                    rank_meme_dic[selected_marble_rank] = [selected_marble,]
                else :
                    print 'EEEERRRRRRR '
            else:
                higher_rank_meme = rank_meme_dic[selected_marble_rank-1][0]
                if fitness_dic[selected_marble] == fitness_dic[higher_rank_meme]:
                    rank_meme_dic[selected_marble_rank-1].append(selected_marble)
                elif fitness_dic[selected_marble] < fitness_dic[higher_rank_meme]:
                    rank_meme_dic = self.shift_dic_down(rank_meme_dic,selected_marble_rank)
                    rank_meme_dic[selected_marble_rank] = [selected_marble,]

    def init_urn(self,marble_fitness,urn_size,fitness_dic,rank_meme_dic,sample_type):
        for n in range(urn_size):
            flag = 0
            while flag ==0:
                fitness = self.generate_fitness(sample_type)
                if not fitness_dic.has_key(fitness):
                    fitness_dic[fitness] = 1
                    rank_meme_dic[1].append(fitness)
                    marble_fitness[n] = fitness
                    flag = 1
  
    def generate_fitness(self,sample_type):
        if sample_type == 'uniform':
            fitness = np.random.random_sample()
        return fitness

    def pick_method(self,fitness_dic,rank_meme_dic,time_step,beta,alpha):
        random_number = random.random()
        if random_number < beta:
            self.pick_quality(fitness_dic,rank_meme_dic)
        else:
	    if alpha == 10:
		self.pick_preferntial_attachment(fitness_dic,rank_meme_dic)
	    else:
	        self.pick_ranking_model(fitness_dic,rank_meme_dic,alpha)

    def pick_preferntial_attachment(self,fitness_dic,rank_meme_dic):
        sum_fitness_count = 0
        for fitness in fitness_dic:
            sum_fitness_count += fitness_dic[fitness]
        fitness_count_prob = []
        fitness_list = []
        for fitness in fitness_dic:
            prob = float(fitness_dic[fitness])/sum_fitness_count
            fitness_count_prob.append(prob)
            fitness_list.append(fitness)
        selected_marble = np.random.choice(fitness_list, 1, p=fitness_count_prob)
        fitness_dic[selected_marble[0]] = fitness_dic[selected_marble[0]] + 1
        ###self.update_rank(selected_marble[0],rank_meme_dic,fitness_dic)

    def pick_quality(self,fitness_dic,rank_meme_dic):
        sum_fitness = 0
        for fitness in fitness_dic:
            sum_fitness += fitness
        fitness_prob = []
        fitness_list = []
        for fitness in fitness_dic:
            prob = fitness/sum_fitness
            fitness_prob.append(prob)
            fitness_list.append(fitness)
        selected_marble = np.random.choice(fitness_list, 1, p=fitness_prob)
        fitness_dic[selected_marble[0]] = fitness_dic[selected_marble[0]] + 1
        self.update_rank(selected_marble[0],rank_meme_dic,fitness_dic)

    def pick_ranking_model(self,fitness_dic,rank_meme_dic,alpha):
        actual_rank_meme_dic = self.get_actual_rank(rank_meme_dic)
        alpha_rev = -1 * alpha
        meme_prob_dic = {}
        sum_ranks = 0
        for i in actual_rank_meme_dic:
            for j in range(len(actual_rank_meme_dic[i])):
                sum_ranks += math.pow(float(i),alpha_rev)
        for r in actual_rank_meme_dic.keys():
            for j in range(len(actual_rank_meme_dic[r])):
                    meme = actual_rank_meme_dic[r][j]
                    meme_before = actual_rank_meme_dic[r][j-1]
                    prob = float(math.pow(float(r),alpha_rev))/sum_ranks
                    meme_prob_dic[meme] = prob#/len(actual_rank_meme_dic[r])
        selected_marble = np.random.choice(meme_prob_dic.keys(), 1, p = meme_prob_dic.values())
        fitness_dic[selected_marble[0]] = fitness_dic[selected_marble[0]]+1
        self.update_rank(selected_marble[0],rank_meme_dic,fitness_dic)

    def get_actual_rank(self,rank_meme_dic):
        key = 1
        actual_rank_meme_dic = {}
        for i in rank_meme_dic:
            if i == 1:
                actual_rank_meme_dic[i] = rank_meme_dic[i]
            else:
                key += len(rank_meme_dic[i-1])
                actual_rank_meme_dic[key] = rank_meme_dic[i]
        return actual_rank_meme_dic

    def running_average(self,fitness_dic):
        sum_qc = 0.0
        sum_c = 0.0
        for fitness in fitness_dic:
            sum_qc += fitness * fitness_dic[fitness]
            sum_c += fitness_dic[fitness]
        mean_quality = sum_qc/sum_c
        return mean_quality
  
    def sim_urn(self,urn_size, simulation_time,beta, alpha,sample_type):
        fitness_dic = {}  # keys are fitness, values are count of fitness
        marble_fitness = {}
        rank_meme_dic = {}  #keys are rank, values are list of fitness
        tracking_meme_dic = {} # keys are fitness, values are the list of tuple (-1,timestep) or (+,timestep)
        rank_meme_dic[1] = []
        time_running_average = {}
	ave_quality = 0
        time_step = 0
        time_size_dic = {}
        self.init_urn(marble_fitness,urn_size,fitness_dic,rank_meme_dic,sample_type)
        #pickle.dump(marble_fitness,open(urn_file,'wb'))
        while time_step <  simulation_time :
            time_step += 1
            self.pick_method(fitness_dic,rank_meme_dic,time_step,beta,alpha)
            if time_step % urn_size == 0:
                time_running_average[time_step] = self.running_average(fitness_dic)
		ave_quality = time_running_average[time_step]
        return ave_quality,fitness_dic

    def sim_prefential_attachemnt(self,urn_size, simulation_time,beta, alpha,sample_type):
        fitness_dic = {}  # keys are fitness, values are count of fitness
        marble_fitness = {}
        rank_meme_dic = {}  #keys are rank, values are list of fitness
        tracking_meme_dic = {} # keys are fitness, values are the list of tuple (-1,timestep) or (+,timestep)
        rank_meme_dic[1] = []
        time_running_average = {}
        ave_quality = 0
        time_step = 0
        time_size_dic = {}
        self.init_urn(marble_fitness,urn_size,fitness_dic,rank_meme_dic,sample_type)
        #pickle.dump(marble_fitness,open(urn_file,'wb'))
        while time_step <  simulation_time :
            time_step += 1
            self.pick_method(fitness_dic,rank_meme_dic,time_step,beta,alpha)
            if time_step % urn_size == 0:
                time_running_average[time_step] = self.running_average(fitness_dic)
                ave_quality = time_running_average[time_step]
        return ave_quality,fitness_dic
       
 
