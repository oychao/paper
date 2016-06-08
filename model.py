# -*- coding: utf-8 -*-
import time
import math
import numpy as np
import pandas as pd
import operator
import data


def qos_time(matrix_data, gene):
    """
    QoS之一,计算Web服务质量的服务器响应时间因素
    :param matrix_data:
    :param gene:
    :return:
    """
    score = 0
    for i in range(len(gene)):
        score += matrix_data[i][data.columns[0]][gene[i]]
    return score


def qos_cost(matrix_data, gene):
    """
    QoS之一,计算Web服务质量的价格成本因素
    :param matrix_data:
    :param gene:
    :return:
    """
    score = 0
    for i in range(len(gene)):
        score += matrix_data[i][data.columns[1]][gene[i]]
    return score


def qos_availability(matrix_data, gene):
    """
    QoS之一,计算Web服务质量的可用性因素
    :param matrix_data:
    :param gene:
    :return:
    """
    score = 1
    for i in range(len(gene)):
        score *= matrix_data[i][data.columns[2]][gene[i]]
    return score


def qos_reliability(matrix_data, gene):
    """
    QoS之一,计算Web服务质量的可靠性因素
    :param matrix_data:
    :param gene:
    :return:
    """
    score = 1
    for i in range(len(gene)):
        score *= matrix_data[i][data.columns[3]][gene[i]]
    return score


def qos_reputation(matrix_data, gene):
    """
    QoS之一,计算Web服务质量的名誉度因素
    :param matrix_data:
    :param gene:
    :return:
    """
    score = 1
    for i in range(len(gene)):
        score += matrix_data[i][data.columns[3]][gene[i]]
    return score / len(gene)


def qos_total(matrix_data, gene):
    """
    线性加权计算QoS总质量,暂定权值均为0.2,满足权值和为1
    :param matrix_data:
    :param gene:
    :return:
    """
    result = 0.1 * qos_time(matrix_data, gene)
    result += 0.1 * qos_cost(matrix_data, gene)
    result += 0.3 * qos_availability(matrix_data, gene)
    result += 0.3 * qos_reliability(matrix_data, gene)
    result += 0.2 * qos_reputation(matrix_data, gene)
    return result


def best_qos(matrix_data):
    """
    获取最佳服务质量及其解,
    本函数采用穷举法,及其消耗时间
    :param matrix_data:
    :return:
    """

    def self_plus(index=-2):
        """
        自加1
        :param index:
        :return:
        """
        if index == -1:
            # 迭代结束
            return False
        if index == -2:
            index = len(vec) - 1
        while index >= 0:
            if vec[index] + 1 >= matrix_data[index].shape[0]:
                vec[index] = 0
                self_plus(index - 1)
                break
            else:
                vec[index] += 1
                break
        return True

    # vec = [19, 19, 19, 19, 19, 19]
    # self_plus()
    # if self_plus():
    #     print('test')
    # print(vec)

    vec = []
    vec_pre = []
    vec_best = []
    adaption_best = 0
    for i in range(len(matrix_data)):
        vec.append(0)
        vec_best.append(0)
        vec_pre.append(-1)

    while self_plus():
        adaption_cur = qos_total(matrix_data, vec)
        if adaption_cur > adaption_best:
            adaption_best = adaption_cur
            vec_best = vec[:]
        if vec_pre[2] != vec[2]:
            print(vec_best, adaption_best)
            print(vec)
        vec_pre = vec[:]
    return vec_best, adaption_best


def genetic_optimize(matrix_data, adaptive_function, mutate_prob=0.2, step=1, elite_rate=0.2,
                     max_iter=100):
    """
    经典遗传算法,
    采用选择算子采用排序法,
    变异算子,
    交叉算子采用随机交叉
    :param matrix_data:
    :param adaptive_function:
    :param mutate_prob:
    :param step:
    :param elite_rate:
    :param max_iter:
    :return:
    """

    def mutate(vec):
        """
        变异算子
        :param vec:
        :return:
        """
        m = np.random.randint(0, len(matrix_data))
        if np.random.random() < 0.5:
            # 染色体变异位置超过下限
            if vec[m] - step < 0:
                return vec[0:m] + [0] + vec[m + 1:]
            # 向下变异,移动step个单位
            return vec[0:m] + [vec[m] - step] + vec[m + 1:]
        else:
            # 染色体变异位置超过上限
            if vec[m] + step >= matrix_data[m].shape[0]:
                return vec[0:m] + [matrix_data[m].shape[0] - 1] + vec[m + 1:]
            # 向上变异,移动step个单位
            return vec[0:m] + [vec[m] + step] + vec[m + 1:]

    def cross_over(r1, r2):
        """
        交叉算子
        :param r1:
        :param r2:
        :return:
        """
        m = np.random.randint(1, len(r1) - 2)
        return r1[:m] + r2[m:]

    # 记录算法开始时间戳
    t_begin = time.time()
    # 记录迭代过程
    procedure = []

    # 随机生成初始种群
    population = data.get_population()
    population_size = len(population)

    # 精英数
    top_elite_count = int(elite_rate * population_size)

    # 主循环迭代
    scores = None
    for i in range(max_iter):
        # 获取种群中所有基因的适应度和基因的元组
        scores = [(gene, adaptive_function(matrix_data, gene)) for gene in population]
        scores.sort(reverse=True, key=operator.itemgetter(1))
        procedure.append((scores[0], i + 1, time.time() - t_begin))
        # print(scores[0], i + 1)
        # print(str(i) + '-------------------')
        # for score in scores:
        #     print(score)

        ranked_population = [g for (g, s) in scores]

        # 获取精英基因,淘汰劣质染色体
        population = ranked_population[:top_elite_count]

        while len(population) < population_size:
            if np.random.random() < mutate_prob:
                # 变异
                i = np.random.randint(0, top_elite_count)
                population.append(mutate(ranked_population[i]))
            else:
                # 交叉
                i = np.random.randint(0, top_elite_count)
                k = np.random.randint(0, top_elite_count)
                population.append(cross_over(ranked_population[i], ranked_population[k]))

    # 返回收敛后的解元组(适应度,染色体)
    return procedure


def random_optimize(matrix_data, adaptive_function):
    """
    随机搜索算法
    :param matrix_data:
    :param adaptive_function:
    :return:
    """
    # 记录算法开始时间戳
    t_begin = time.time()
    vec = []
    for i in range(len(matrix_data)):
        vec.append(0)
    v_best = adaptive_function(matrix_data, vec)
    chromosome_best = vec[:]
    # 获取随机点
    population = data.get_population()
    for chromosome in population:
        v_cur = adaptive_function(matrix_data, chromosome)
        if v_best < v_cur:
            v_best = v_cur
            chromosome_best = chromosome[:]
    # 返回元组为(解,值,运行时间)
    return chromosome_best, v_best, time.time() - t_begin


def hill_climbing(matrix_data, adaptive_function, vec):
    """
    爬山算法
    :param matrix_data:
    :param adaptive_function:
    :param vec:
    :return:
    """
    while True:
        neighbours = []
        for k in range(len(vec)):
            if vec[k] + 1 < matrix_data[k].shape[0]:
                neighbours.append(vec[:k] + [vec[k] + 1] + vec[k + 1:])
            if vec[k] - 1 > 0:
                neighbours.append(vec[:k] + [vec[k] - 1] + vec[k + 1:])
        v_best = adaptive_function(matrix_data, vec)
        # vec_best = vec
        for neighbour in neighbours:
            v_cur = adaptive_function(matrix_data, neighbour)
            if v_best < v_cur:
                v_best = v_cur
                # vec_best = neighbour
        return v_best


def random_hill_climbing(matrix_data, adaptive_function):
    """
    随机重复爬山算法
    :param matrix_data:
    :param adaptive_function:
    :return:
    """
    # 记录算法开始时间
    t_begin = time.time()
    # 获取初始随机点
    population = data.get_population()
    best_chromosome = []
    for i in range(len(matrix_data)):
        best_chromosome.append(0)
    best_value = adaptive_function(matrix_data, best_chromosome)
    for chromosome in population:
        cur_value = hill_climbing(matrix_data, adaptive_function, chromosome)
        if cur_value > best_value:
            best_value = cur_value
            best_chromosome = chromosome
    # 返回的元组为(解,值,运行时间)
    return best_chromosome, best_value, time.time() - t_begin


def random_simulated_annealing(matrix_data, adaptive_function, temperature=10000, t_threshold=0.1, cooling_rate=0.1,
                               step=1):
    """
    模拟退火算法
    :param matrix_data:
    :param adaptive_function:
    :param temperature:
    :param t_threshold:
    :param cooling_rate:
    :param step:
    :return:
    """
    # 记录算法开始时间戳
    t_begin = time.time()
    # 获取起始种群
    population = data.get_population()
    best_vec = population[0]
    best_value = adaptive_function(matrix_data, best_vec)
    for vec in population:
        v_origin = 0
        cur_temperature = temperature
        while cur_temperature > t_threshold:
            # 选择一个索引位置
            i = np.random.randint(0, len(vec) - 1)
            # 选择一个改变索引的方向
            direction = np.random.randint(-step, step)
            # 创建新解
            vec_b = vec[:]
            if vec_b[i] + direction >= matrix_data[i].shape[0]:
                vec_b[i] = matrix_data[i].shape[0]
            elif vec_b[i] + direction < 0:
                vec_b[i] = 0
            else:
                vec_b[i] += direction

            # 当前解的目标函数
            v_origin = adaptive_function(matrix_data, vec)
            # 新解的目标函数
            v_b = adaptive_function(matrix_data, vec_b)

            # 接受更好的解,或者温度高时有一定概率接受更差的解
            if v_origin < v_b or np.random.random() < pow(math.e, -(v_b - v_origin) / cur_temperature):
                vec = vec_b

            # 降温
            cur_temperature *= cooling_rate
        # 记录最佳值和解
        if v_origin > best_value:
            best_value = v_origin
            best_vec = vec
    # 返回元组为(解,值,运行时间)
    return best_vec, best_value, time.time() - t_begin


def particle_swarm_optimize(matrix_data, adaptive_function, max_iter=100, weight=0.8, c1=2, c2=2):
    """
    一种改进的粒子群优化算法
    :param matrix_data:
    :param adaptive_function:
    :param max_iter:
    :param weight:
    :param c1:
    :param c2:
    :return:
    """
    # 算法开始时间戳
    t_begin = time.time()
    # 记录迭代状态
    procedure = []
    # 粒子群
    population = data.get_population()
    # 随机速度
    speeds = data.generate_population(matrix_data, len(population))
    # 每个粒子的最佳纪录
    best_histories = []
    # 粒子群的最佳纪录
    best_of_all = (None, 0)
    # 初始化每个粒子的最佳纪录
    for chromosome in population:
        value_cur = adaptive_function(matrix_data, chromosome)
        best_histories.append((chromosome, value_cur))
        if value_cur > best_of_all[1]:
            best_of_all = (chromosome, value_cur)
    # 主循环
    for i in range(max_iter):
        procedure.append((best_of_all, i + 1, time.time() - t_begin))
        # print(best_of_all, i)
        # print(best_histories[0])
        # print(population[0])
        # print(speeds[0])
        # print('')
        for k in range(len(population)):
            chromosome = population[k]
            speed = speeds[k]
            for m in range(len(chromosome)):
                # 计算速度
                speed[m] *= speed[m] * weight
                speed[m] += c1 * np.random.random() * (best_histories[k][0][m] - chromosome[m])
                speed[m] += c2 * np.random.random() * (best_of_all[0][m] - chromosome[m])
                speed[m] = int(round(speed[m])) % matrix_data[m].shape[0]
                # 计算新的位置
                chromosome[m] += speed[m]
                chromosome[m] %= matrix_data[m].shape[0]

                # if chromosome[m] + speed[m] >= matrix_data[m].shape[0]:
                #     chromosome[m] = matrix_data[m].shape[0] - 1
                # elif chromosome[m] + speed[m] < 0:
                #     chromosome[m] = 0
                # else:
                #     chromosome[m] += speed[m]
            value_cur = adaptive_function(matrix_data, chromosome)
            if value_cur > best_histories[k][1]:
                best_histories[k] = (chromosome, value_cur)
            if value_cur > best_of_all[1]:
                # print('updated')
                best_of_all = (chromosome[:], value_cur)

    procedure.append((best_of_all, i + 1, time.time() - t_begin))

    return procedure


def improved_ga(matrix_data, adaptive_function, chromosome_mutate_rate=0.2, step=1, elite_rate=0.2,
                max_iter=100, temperature=10000, threshold_mutate_prob=0.1, cooling_rate=0.8):
    """
    变异算子经过改进的遗传算法,
    选择算子采用模拟退火思想,
    变异算子遍历选取局部最优解,
    交叉算子采用随机交叉
    :param matrix_data:目标矩阵
    :param adaptive_function:适应度函数
    :param chromosome_mutate_rate: 每次变异时,染色体中有chromosome_mutate_rate的比例的基因将会发生突变
    :param step:单个基因变异移动步骤
    :param elite_rate:精英留存率
    :param max_iter:最大迭代次数
    :param temperature:温度
    :param threshold_mutate_prob:最高变异率
    :param cooling_rate:冷却率
    :return:
    """

    # def mutate(vec):
    #     """
    #     变异算子
    #     :param vec:染色体
    #     :return:
    #     """
    #     m = np.random.randint(0, len(matrix_data))
    #     cur_vec = vec[0:m] + [(vec[m] - step + matrix_data[m].shape[0]) % matrix_data[m].shape[0]] + vec[m + 1:]
    #     best_val = adaptive_function(matrix_data, cur_vec)
    #     # temp = best_val
    #     best_vec = cur_vec
    #     for n in range(int(chromosome_mutate_rate * len(vec))):
    #         m = np.random.randint(0, len(matrix_data))
    #         if np.random.random() < 0.5:
    #             # 向下变异,移动step个单位
    #             cur_vec = vec[0:m] + [(vec[m] - step + matrix_data[m].shape[0]) % matrix_data[m].shape[0]] + vec[m + 1:]
    #         else:
    #             # 向上变异,移动step个单位
    #             cur_vec = vec[0:m] + [(vec[m] + step) % matrix_data[m].shape[0]] + vec[m + 1:]
    #         cur_val = adaptive_function(matrix_data, cur_vec)
    #         if cur_val > best_val:
    #             best_val = cur_val
    #             best_vec = cur_vec[:]
    #     # print(temp, best_val)
    #     return best_vec

    # def mutate2(vec):
    #     """
    #     终极大杀器,
    #     当前模型不好,
    #     基因之间不相关,
    #     每个基因都有自己的最佳编码,
    #     因此只要获取染色体的各个基因位置各自的最佳编码,
    #     该染色体就是最佳染色体(最优解),
    #     嘛,写论文的时候我是不会写进去的...哈哈...
    #     改进过的变异算子
    #     随机基因位置,
    #     确定该基因最合适编码
    #     :param vec:
    #     :return:
    #     """
    #     m = np.random.randint(0, len(matrix_data))
    #     best_chromosome = 0
    #     best_v = 0
    #     for index in range(0, matrix_data[m].shape[0]):
    #         cur_v = adaptive_function(matrix_data, vec[0:m] + [index] + vec[m + 1:])
    #         if cur_v > best_v:
    #             best_v = cur_v
    #             best_chromosome = vec[0:m] + [index] + vec[m + 1:]
    #     return best_chromosome

    def mutate(vec, accept_prob=0):
        """
        改进过的变异算子,
        随机基因位置,
        确定该基因最合适编码
        :param vec:
        :param accept_prob:
        :return:
        """
        m = np.random.randint(0, len(matrix_data))
        best_val = 0
        g_index = np.random.randint(0, matrix_data[m].shape[0])
        best_vec = None
        while True:
            cur_vec = vec[0:m] + [g_index] + vec[m + 1:]
            cur_val = adaptive_function(matrix_data, cur_vec)
            if best_val < cur_val or np.random.random() < accept_prob:
                best_val = cur_val
                best_vec = cur_vec[:]
            else:
                break
        return best_vec

    # def mutate3(vec):
    #     """
    #     改进过的变异算子,
    #     随机基因位置,
    #     确定该基因最合适编码
    #     :param vec:
    #     :return:
    #     """
    #     m = np.random.randint(0, len(matrix_data))
    #     best_val = 0
    #     g_index = np.random.randint(0, matrix_data[m].shape[0])
    #     best_vec = None
    #     while True:
    #         cur_vec = vec[0:m] + [g_index] + vec[m + 1:]
    #         cur_val = adaptive_function(matrix_data, cur_vec)
    #         if best_val < cur_val:
    #             best_val = cur_val
    #             best_vec = cur_vec[:]
    #         else:
    #             break
    #     return best_vec

    def cross_over(r1, r2):
        """
        交叉算子
        :param r1:
        :param r2:
        :return:
        """
        result = []
        for m in range(len(r1)):
            if np.random.random() > 0.5:
                result.append(r1[m])
            else:
                result.append(r2[m])
        return result

    # 记录算法开始时间戳
    t_begin = time.time()

    # 记录每一代的最优状态
    procedure = []

    # 随机生成初始种群
    population = data.get_population()
    population_size = len(population)

    # 精英数
    top_elite_count = int(elite_rate * population_size)

    # 主循环迭代
    scores = None
    for i in range(max_iter):
        # 获取种群中所有基因的适应度和基因的元组
        scores = [(gene, adaptive_function(matrix_data, gene)) for gene in population]
        scores.sort(reverse=True, key=operator.itemgetter(1))
        procedure.append((scores[0], i + 1, time.time() - t_begin))
        # print(scores[0], i + 1)
        # print(str(i) + '-------------------')
        # for score in scores:
        #     print(score)

        ranked_population = [g for (g, v) in scores]

        # 动态计算变异率,模拟退火算法计算变异率,如得到的变异率大于设定的最低变异率,则按最低变异率按最大变异率计算
        population = ranked_population[:top_elite_count]
        mutate_prob = 1 - pow(math.e, -(scores[top_elite_count - 1][1] - scores[0][1])) / temperature
        if threshold_mutate_prob > mutate_prob:
            mutate_prob = threshold_mutate_prob
        else:
            # 降温
            temperature *= cooling_rate
        # 获取精英基因,淘汰劣质染色体
        while len(population) < population_size:
            if np.random.random() < mutate_prob:
                # 变异
                i = np.random.randint(0, top_elite_count)
                population.append(mutate(ranked_population[i], 1 - mutate_prob))
            else:
                # 交叉
                i = np.random.randint(0, top_elite_count)
                k = np.random.randint(0, top_elite_count)
                population.append(cross_over(ranked_population[i], ranked_population[k]))

                # 返回收敛后的解元组(适应度,染色体)
    # 返回的元组((解,值),代数,运行时间)
    return procedure


def print_array(arr):
    """
    打印数组
    :param arr:
    :return:
    """
    for l in arr:
        print(l)


if __name__ == '__main__':
    # 读取仿真数据矩阵的数组
    simulation_data = []
    for j in range(data.class_length):
        simulation_data.append(pd.read_csv(data.dt_path(j), index_col=0))

    '''
    各个算法重复20次试验并保存结果

    每次实验分别运行6个算法
    随机搜索...1
    重复爬山...2
    重复模拟退火...3
    改进后的遗传算法(目标算法)...4
    遗传算法...5
    粒子群优化...6

    实验结果元组格式为(解,值,运行时间)
    其中算法4,5,6保存每一次迭代的状态

    每次算法1,2,3的初始随机解即群体智能算法(算法4,5,6)的初始种群
    此外每次实验的初始种群(初始随机解)重新生成一次
    '''
    # 实验总用时起始时间戳
    t_begin = time.time()
    # 实验的种群大小
    population_size = 200
    for index in range(20, 21):
        # 生成初始种群(初始随机解)
        data.generate_population(simulation_data, population_size)

        # 随机搜索
        print('random search ' + str(index))
        result = random_optimize(simulation_data, qos_total)
        path = 'result/' + str(index) + '_1_random_search.pkl'
        data.write_result(path, result)
        # print(data.read_result(path))

        # 重复爬山
        print('random restart hill climbing ' + str(index))
        result = random_hill_climbing(simulation_data, qos_total)
        path = 'result/' + str(index) + '_2_random_restart_hill_climbing.pkl'
        data.write_result(path, result)
        # print(data.read_result(path))

        # 重复模拟退火
        print('simulated annealing ' + str(index))
        result = random_simulated_annealing(simulation_data, qos_total)
        path = 'result/' + str(index) + '_3_simulated_annealing.pkl'
        data.write_result(path, result)
        # print(data.read_result(path))

        # 改进后的遗传算法
        print('improved generic algorithm ' + str(index))
        result = improved_ga(simulation_data, qos_total, max_iter=100, threshold_mutate_prob=0.95)
        path = 'result/' + str(index) + '_4_improved_generic_algorithm.pkl'
        data.write_result(path, result)
        # print_array(data.read_result(path))

        # 遗传算法
        print('generic algorithm ' + str(index))
        result = genetic_optimize(simulation_data, qos_total, max_iter=100, mutate_prob=0.95, step=4)
        path = 'result/' + str(index) + '_5_generic_algorithm.pkl'
        data.write_result(path, result)
        # print_array(data.read_result(path))

        # 粒子群优化
        print('particle swarm optimization ' + str(index))
        result = particle_swarm_optimize(simulation_data, qos_total, max_iter=200)
        path = 'result/' + str(index) + '_6_generic_algorithm.pkl'
        data.write_result(path, result)
        # print_array(data.read_result(path))

    # 总用时
    print(time.time() - t_begin)
