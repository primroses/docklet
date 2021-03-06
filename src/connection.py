# coding=UTF-8
#!/usr/bin/python
# -*- coding: UTF-8 -*-

import zmq
import time
from log import slogger

task_ctx = None
task_s = None

colony_ctx = None
colony_s = None

result_ctx = None
result_s = None

sync_ctx = None
sync_s = None

def init_task_socket():
    global task_ctx
    global task_s
    bind_to = "tcp://*:5000"
    task_ctx = zmq.Context().instance()
    task_s = task_ctx.socket(zmq.PUB)
    task_s.bind(bind_to)

def init_sync_socket():
    global sync_ctx
    global sync_s

    sync_with = "tcp://*:5001"
    sync_ctx = zmq.Context.instance()
    slogger.debug("ctx max_sockets: %d",sync_ctx.get(zmq.MAX_SOCKETS))
    sync_ctx.set(zmq.MAX_SOCKETS, 65536)
    slogger.debug("ctx max_sockets: %d",sync_ctx.get(zmq.MAX_SOCKETS))
    sync_s = sync_ctx.socket(zmq.REP)
    sync_s.bind(sync_with)
    slogger.debug("Waiting for subscriber to connect...")

def sync_colony():
    id = sync_s.recv_string()
    slogger.debug("done sync with %s", id)
    sync_s.send_string("sync success")
    slogger.info("colony %s synced",id);

def send_task(machine,task, oper):

#    slogger.debug("Sending new task %s to machine %s, operation:%s  ... " ,task['id'],  machine.machineid, oper)
    task_s.send_string(str(machine.machineid) + " ",zmq.SNDMORE)
    task_s.send_string(str(task['id']),zmq.SNDMORE)
    task_s.send_string(str(task['cpus']),zmq.SNDMORE)
    task_s.send_string(str(task['mems']),zmq.SNDMORE)
    task_s.send_string(str(task['bid']),zmq.SNDMORE)
    task_s.send_string(oper)

#    slogger.debug("Done.")

def init_colony_socket():
    global colony_ctx
    global colony_s
    colony_ctx = zmq.Context.instance()
    colony_s = colony_ctx.socket(zmq.REQ)
    colony_s.connect("tcp://localhost:5002")
    slogger.debug("colony socket ready")
    colony_s.send_string("colony socket ready")
    sync_result = colony_s.recv_string()
    slogger.info("colony sync_result: %s",sync_result)

def send_colony(oper, id, cpus, mems,):
    colony_s.send_string(oper,zmq.SNDMORE)
    colony_s.send_string(id,zmq.SNDMORE)
    colony_s.send_string(cpus,zmq.SNDMORE);
    colony_s.send_string(mems);
    reply = colony_s.recv_string()
    slogger.debug("create colony %s reply: %s",id,reply)

def init_result_socket():
    global result_ctx
    global result_s
    result_ctx = zmq.Context.instance()

    slogger.debug("ctx max_sockets: %d",result_ctx.get(zmq.MAX_SOCKETS))
    sync_ctx.set(zmq.MAX_SOCKETS, 65536)
    slogger.debug("ctx max_sockets: %d",result_ctx.get(zmq.MAX_SOCKETS))

    result_s = result_ctx.socket(zmq.REP)
    result_s.bind("tcp://*:5003")
    slogger.info("result recv socklet created!")


def recv_result(machines):
    while(True):
        slogger.debug("waiting for result!")
        machineid = result_s.recv_string()
        solution_str = result_s.recv_string()
        mem_value_str = result_s.recv_string()
        ratio_str = result_s.recv_string()

        mem_value = float(mem_value_str)
        ratio = float(ratio_str)
        slogger.info("recv_string result of machine %s: %s %e %e", machineid, solution_str, mem_value, ratio)
        result_s.send_string("success")
        machine = machines[machineid]
        machine.mem_value = mem_value
        machine.cpu_value = mem_value * ratio
        machine.change_reliable_allocations(solution_str);

def test_pub_socket():
    generate_test_data(64,256,1)
#    tasks = parse_test_data()
    init_machines(64, 256, 1)
    dispatch(tasks);
#    test3()

def test_colony_socket():
    init_mmdkp_socket()
    send_colony("add","0","64","256")
