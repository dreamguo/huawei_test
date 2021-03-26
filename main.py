#!/usr/bin/env python
# -*- coding:utf-8 -*-
import sys
import numpy as np
# import line_profiler

server_dict = {}
vm_dict = {}

class Server:
    def __init__(self, name, CPU, memory, purchase_cost, daliy_cost, id=None):
        self.name = name
        self.A_CPU = int(int(CPU) / 2)
        self.B_CPU = self.A_CPU
        self.A_memory = int(int(memory) / 2)
        self.B_memory = self.A_memory
        self.purchase_cost = int(purchase_cost)
        self.daliy_cost = int(daliy_cost)
        self.id = id

    def display(self):
        print("{}:{}, purchase_cost:{} daliy_cost:{}".format(
                self.id, self.name, self.purchase_cost, self.daliy_cost))
        print("         A_CPU:{}      A_memory:{}      B_CPU:{}      B_memory:{}".format(
                self.A_CPU, self.A_memory, self.B_CPU, self.B_memory))

    def total_cost(self, left_day):
        return self.purchase_cost + self.daliy_cost * left_day

    def load(self, vm, node):
        if node == 'A':
            self.A_CPU -= vm.CPU
            self.A_memory -= vm.memory
        elif node == 'B':
            self.B_CPU -= vm.CPU
            self.B_memory -= vm.memory
        elif node == "AB":
            self.A_CPU -= vm.CPU
            self.A_memory -= vm.memory
            self.B_CPU -= vm.CPU
            self.B_memory -= vm.memory
        vm.load(self.id, node)

    def release(self, vm):
        if vm.node == 'A':
            self.A_CPU += vm.CPU
            self.A_memory += vm.memory
        elif vm.node == 'B':
            self.B_CPU += vm.CPU
            self.B_memory += vm.memory
        elif vm.node == "AB":
            self.A_CPU += vm.CPU
            self.A_memory += vm.memory
            self.B_CPU += vm.CPU
            self.B_memory += vm.memory


class VirtualMachine:
    def __init__(self, name, CPU, memory, double_note, id):
        self.name = name
        self.double_note = double_note == '1'
        if self.double_note:
            self.CPU = int(int(CPU) / 2)
            self.memory = int(int(memory) / 2)
        else:
            self.CPU = int(CPU)
            self.memory = int(memory)
        self.id = id
        self.server_id = None
        self.node = None

    def display(self):
        print("{}, CPU:{} memory:{} double_note:{} server_id:{} node:{}".format(
            self.name, self.CPU, self.memory, self.double_note, self.server_id, self.node))

    def load(self, server_id, node):
        self.server_id = server_id
        self.node = node


def try_load(server_list, vm_list, test=True, display=False):
    # TODO{sort vms by CPU num and memory size? And double-note first?}
    if len(server_list) == 0:
        return vm_list
    left_vms = []
    not_enough = 10
    if test:
        assert isinstance(server_list, tuple)
        A_CPU = int(int(server_list[1]) / 2)
        A_memory = int(int(server_list[2]) / 2)
        B_CPU = A_CPU
        B_memory = A_memory
        left_vms = vm_list.copy()
        for vm_item in vm_list:
            if (A_CPU < not_enough or A_memory < not_enough) and (B_CPU < not_enough or B_memory < not_enough):
                break
            if vm_item.double_note:
                if display:
                    print(vm_item.display())
                if vm_item.CPU <= A_CPU and vm_item.memory <= A_memory and \
                        vm_item.CPU <= B_CPU and vm_item.memory <= B_memory:
                    if display:
                        print("enter")
                    A_CPU -= vm_item.CPU
                    A_memory -= vm_item.memory
                    B_CPU -= vm_item.CPU
                    B_memory -= vm_item.memory
                    left_vms.remove(vm_item)
            else:
                if vm_item.CPU <= A_CPU and vm_item.memory <= A_memory:
                    A_CPU -= vm_item.CPU
                    A_memory -= vm_item.memory
                    left_vms.remove(vm_item)
                else:
                    if vm_item.CPU <= B_CPU and vm_item.memory <= B_memory:
                        B_CPU -= vm_item.CPU
                        B_memory -= vm_item.memory
                        left_vms.remove(vm_item)
    else:
        tmp_server_list = []
        for server in server_list:
            if (server.A_CPU >= not_enough and server.A_memory >= not_enough) or (
                    server.B_CPU >= not_enough and server.B_memory >= not_enough):
                tmp_server_list.append(server)
        if display:
            print(len(tmp_server_list))
            for i in tmp_server_list:
                print(i.display())
        for vm_item in vm_list:
            flag = 1
            rm_list = []
            for server_item in tmp_server_list:
                if vm_item.double_note:
                    if vm_item.CPU <= server_item.A_CPU and vm_item.memory <= server_item.A_memory and \
                            vm_item.CPU <= server_item.B_CPU and vm_item.memory <= server_item.B_memory:
                        server_item.load(vm_item, "AB")
                        flag = 0
                        break
                else:
                    if vm_item.CPU <= server_item.A_CPU and vm_item.memory <= server_item.A_memory:
                        server_item.load(vm_item, "A")
                        flag = 0
                        break
                    else:
                        if vm_item.CPU <= server_item.B_CPU and vm_item.memory <= server_item.B_memory:
                            server_item.load(vm_item, "B")
                            flag = 0
                            break
                if (server_item.A_CPU < not_enough or server_item.A_memory < not_enough) and \
                        (server_item.B_CPU < not_enough or server_item.B_memory < not_enough):
                    rm_list.append(server_item)
            for item in rm_list:
                tmp_server_list.remove(item)
            if flag:
                left_vms.append(vm_item)
    return left_vms


def big_server_first(server_name_list):
    def take_memory(elem):
        return server_dict[elem][2]
    # big first
    server_name_list.sort(reverse=True, key=take_memory)
    return server_name_list


def main():
    file_input = True
    debug = False
    # --------------------------------------------------Basic Info--------------------------------------------------- #
    f = open("training-2.txt", "r")
    if file_input:
        server_num = int(f.readline())
    else:
        server_num = int(sys.stdin.readline())
    server_name_list = []
    for i in range(server_num):
        if file_input:
            server_info = f.readline()
        else:
            server_info = sys.stdin.readline()
        server_info = server_info.replace('\n', '').replace('\r', '').replace('(', '').replace(')', '').replace(' ', '').split(',')
        server_name_list.append(server_info[0])
        server_dict[server_info[0]] = (server_info[0], server_info[1], server_info[2], server_info[3],
                                       server_info[4])
    server_name_list = big_server_first(server_name_list)
    # print(server_dict)
    if file_input:
        vm_num = int(f.readline())
    else:
        vm_num = int(sys.stdin.readline())
    for i in range(vm_num):
        if file_input:
            vm_info = f.readline()
        else:
            vm_info = sys.stdin.readline()
        vm_info = vm_info.replace('\n', '').replace('\r', '').replace('(', '').replace(')', '').replace(' ', '').split(',')
        vm_dict[vm_info[0]] = (vm_info[0], vm_info[1], vm_info[2], vm_info[3])
    # print(vm_dict)
    if file_input:
        day_num = int(f.readline())
    else:
        day_num = int(sys.stdin.readline())
    # ----------------------------------------------------Request----------------------------------------------------- #
    vm_run_dict = {}
    server_run_list = []
    output = ''
    all_cost = 0
    for day_idx in range(day_num):
        if debug:
            print("day_idx:", day_idx)
        left_day = day_num - day_idx
        if file_input:
            request_num = int(f.readline())
        else:
            request_num = int(sys.stdin.readline())
        del_vm_list = []
        vm_new_list = []
        server_new_list = []
        for request_idx in range(request_num):
            if file_input:
                request_info = f.readline()
            else:
                request_info = sys.stdin.readline()
            if debug:
                print("---request---::::::", request_info)
            request_info = request_info.replace('\n', '').replace('\r', '').replace('(', '').replace(')', '').replace(' ', '').split(',')
            if request_info[0] == "del":
                del_vm_list.append(request_info[1])
            elif request_info[0] == "add":
                vm_para = vm_dict[request_info[1]]
                vm = VirtualMachine(vm_para[0], vm_para[1], vm_para[2], vm_para[3], request_info[2])
                vm_run_dict[request_info[2]] = vm
                vm_new_list.append(vm)
            if debug:
                print(vm_run_dict)
    # ----------------------------------------------Dynamic programming----------------------------------------------- #
        init_left_vms = try_load(server_run_list, vm_new_list, test=False)
        best_cost = 99999999999
        best_match = []
        if len(init_left_vms) > 0:
            state_table = np.zeros((server_num, len(init_left_vms)), dtype=np.int).tolist()
            # state_table = [[0 for i in range(10 ** 5)] for j in range(server_num)]
            for server_i in range(server_num):
                # purchase_i is start from 0, mention that we need add 1 when compute it.
                for purchase_i in range(0, len(init_left_vms)):
                    if purchase_i == 0:
                        server_para = server_dict[server_name_list[server_i]]
                        left_vms = try_load(server_para, init_left_vms)
                        cost = int(server_para[3]) + int(server_para[4]) * left_day
                        if cost > best_cost:
                            state_table[server_i][purchase_i] = ([], [], 0)
                            break
                        state_table[server_i][purchase_i] = ([server_name_list[server_i]], left_vms, cost)
                        if len(left_vms) == 0 and cost < best_cost:
                            best_match = state_table[server_i][purchase_i][0]
                            best_cost = cost
                            break
                    else:
                        if server_i == 0:
                            last_server, last_vms, last_cost = state_table[server_i][purchase_i - 1]
                            server_para = server_dict[server_name_list[server_i]]
                            left_vms = try_load(server_para, last_vms)
                            last_server.append(server_name_list[server_i])
                            cost = int(server_para[3]) + int(server_para[4]) * left_day + last_cost
                            state_table[server_i][purchase_i] = (last_server, left_vms, cost)
                            if len(left_vms) == 0 and cost < best_cost:
                                best_match = state_table[server_i][purchase_i][0]
                                best_cost = cost
                                # print(server_i, ", ", purchase_i, ": ",
                                #      state_table[server_i][purchase_i][0])
                                break
                        else:
                            server_para = server_dict[server_name_list[server_i]]
                            # less purchase one
                            if state_table[server_i - 1][purchase_i - 1] != 0:
                                last_server_1, last_vms_1, last_cost_1 = state_table[server_i - 1][purchase_i - 1]
                                if len(last_server_1) != 0:
                                    left_vms_1 = try_load(server_para, last_vms_1)
                                    # last server one
                                    last_server_2, last_vms_2, last_cost_2 = state_table[server_i][purchase_i - 1]
                                    left_vms_2 = try_load(server_para, last_vms_2)
                                    # judge which one is better TODO{many ways to define}
                                    if len(left_vms_1) <= len(left_vms_2):
                                        last_server = last_server_1
                                        left_vms = left_vms_1
                                        last_cost = last_cost_1
                                    else:
                                        last_server = last_server_2
                                        left_vms = left_vms_2
                                        last_cost = last_cost_2
                                else:
                                    last_server, last_vms, last_cost = state_table[server_i][purchase_i - 1]
                            else:
                                last_server, last_vms, last_cost = state_table[server_i][purchase_i - 1]
                            last_server.append(server_name_list[server_i])
                            cost = int(server_para[3]) + int(server_para[4]) * left_day + last_cost
                            if cost > best_cost:
                                if state_table[server_i - 1][purchase_i] != 0:
                                    _, _, last_cost = state_table[server_i - 1][purchase_i]
                                    assert int(server_para[3]) + int(server_para[4]) * left_day + last_cost
                                state_table[server_i][purchase_i] = ([], [], 0)
                                break
                            state_table[server_i][purchase_i] = (last_server, left_vms, cost)
                            if len(left_vms) == 0 and cost < best_cost:
                                best_match = state_table[server_i][purchase_i][0]
                                best_cost = cost
                                if debug:
                                    print(server_i, ", ", purchase_i, ": ", best_match)
                                break
            all_cost += best_cost
            # print(best_cost)
            for server_name in best_match:
                server_para = server_dict[server_name]
                server = Server(server_para[0], server_para[1], server_para[2], server_para[3],
                                server_para[4], id=len(server_run_list))
                server_run_list.append(server)
                server_new_list.append(server)
            left_vms = try_load(server_new_list, init_left_vms, test=False, display=debug)
            if debug:
                print("----------------------------")
                print(len(init_left_vms))
                for i in init_left_vms:
                    print(i.display())
                print(len(left_vms))
                for i in left_vms:
                    print(i.display())
                for i in server_new_list:
                    print(i.display())
            assert len(left_vms) == 0
        for del_vm in del_vm_list:
            vm = vm_run_dict.pop(del_vm)
            server_run_list[vm.server_id].release(vm)
    # ----------------------------------------------------output----------------------------------------------------- #
        best_match_dict = {}
        class_num = 0
        for server_name in best_match:
            if server_name not in best_match_dict.keys():
                best_match_dict[server_name] = 1
                class_num += 1
            else:
                best_match_dict[server_name] += 1
        output += "(purchase, {})\n".format(class_num)
        for server_name in best_match_dict.keys():
            output += "({}, {})\n".format(server_name, best_match_dict[server_name])
        output += "(migration, 0)\n".format()
        for vm in vm_new_list:
            if vm.double_note:
                output += "({})\n".format(vm.server_id)
            else:
                output += "({}, {})\n".format(vm.server_id, vm.node)
    sys.stdout.write(output)
    sys.stdout.flush()
    print("all_cost: ", all_cost)

if __name__ == '__main__':

    # profile = line_profiler.LineProfiler(main)
    # profile.enable()  # 开始分析
    main()
    # profile.disable()  # 停止分析
    # profile.print_stats()  # 打印出性能分析结果
