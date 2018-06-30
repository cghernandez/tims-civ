import networkx as nx
import matplotlib.pyplot as plt
import random
import scipy.sparse as sp
import numpy as np
import sys

ncities = int(sys.argv[1])
cutoffr = int(sys.argv[2])

def create_cities(maxx,maxy,ncities,minpop,maxpop,minres,maxres,r):
    usados = []
    G_pop = nx.DiGraph()
    G_res = nx.DiGraph()
    count = 0

    with open("WORLDMAP.txt","r") as f:
        leer = True

        while leer:
            l = f.readline().strip("\n").split(",")

            if l == [""]:
                leer = False
                continue

            l = list(map(int,l))

            x,y,rate = l

            G_pop.add_node(
                    count,
                    pop     = random.randint(minpop,maxpop),
                    pos     = (x,y))

            G_res.add_node(
                    count,
                    res     = random.randint(minres,maxres),
                    e_rate  = rate,
                    pos     = (x,y))

            usados.append((x,y))
            count += 1

    while count < ncities:

        x = random.randint(0,maxx)
        y = random.randint(0,maxy)

        if (x,y) in usados:
            continue

        r2 = r**2

        descartar = True

        for i in range(len(G_pop)):
            d2 = ((x - G_pop.nodes[i]["pos"][0])**2 + 
                    (y - G_pop.nodes[i]["pos"][1])**2)

            if d2 < r2:
                descartar = False
                break

        if descartar:
            continue

        G_pop.add_node(
                count, 
                pop     = random.randint(minpop,maxpop),
                pos     = (x,y))

        G_res.add_node(
                count,
                res     = random.randint(minres, maxres),
                e_rate  = 0,
                pos     = (x,y))

        usados.append((x,y))

        count += 1

    return G_pop, G_res

def connect(G,r):
    r2 = r**2
    
    for i in range(len(G)):
        
        for j in range(len(G)):

            if i == j:
                continue

            d2 = ((G.nodes[i]["pos"][0] - G.nodes[j]["pos"][0])**2 + 
                    (G.nodes[i]["pos"][1] - G.nodes[j]["pos"][1])**2)

            if d2 < r2:
                w = (1 - d2/r2)**2
                G.add_edge(i, j, weight = w)
                G[i][j]["weight0"] = w

def update_weights(G_pop,G_res):

    for i,j in G_pop.edges():

        ipc = G_res.nodes[i]["res"]/(G_pop.nodes[i]["pop"] + .01)
        jpc = G_res.nodes[j]["res"]/(G_pop.nodes[j]["pop"] + .01)

        G_pop[i][j]["weight"] = G_pop[i][j]["weight0"]*jpc/(ipc + jpc + 0.01)
        G_res[i][j]["weight"] = G_res[i][j]["weight0"]*ipc/(ipc + jpc + 0.01)


def evolve(G_pop, G_res, steps, gamma, r, k):

    state_pop = np.zeros((steps,len(G_pop)))
    state_res = np.zeros((steps,len(G_res)))

    lerate = np.array(list(
        nx.get_node_attributes(G_res,"e_rate").values()))

    for t in range(steps):

        A_pop = np.transpose(nx.adjacency_matrix(G_pop))
        D_pop = sp.eye(len(G_pop))
        D_pop.setdiag([j for i,j in G_pop.out_degree(weight="weight")])
        L_pop = D_pop - A_pop

        A_res = np.transpose(nx.adjacency_matrix(G_res))
        D_res = sp.eye(len(G_res))
        D_res.setdiag([j for i,j in G_res.out_degree(weight="weight")])
        L_res = D_res - A_res


        lpop = np.array(list(
            nx.get_node_attributes(G_pop,"pop").values()))

        lres = np.array(list(
            nx.get_node_attributes(G_res,"res").values()))

        state_pop[t] = lpop
        state_res[t] = lres

        dlpop = -gamma*L_pop.dot(lpop) + r*lpop*(1 - lpop/(k*(lres + 0.01)))
        dlres = -gamma*L_res.dot(lres) + 0.04*lerate - 0.02*lpop

        lpop = lpop + dlpop
        lres = lres + dlres

        lpop[lpop < 0] = 0
        lres[lres < 0] = 0

        nx.set_node_attributes(G_pop,dict(enumerate(lpop)),"pop")
        nx.set_node_attributes(G_res,dict(enumerate(lres)),"res")
        
        update_weights(G_pop,G_res)

    lpop = lpop.astype(int)
    lres = lres.astype(int)

    state_pop[-1] = lpop
    state_res[-1] = lres

    nx.set_node_attributes(G_pop,dict(enumerate(lpop)),"pop")
    nx.set_node_attributes(G_res,dict(enumerate(lres)),"res")

    return (state_pop,state_res)


G_population, G_resources = create_cities(
        100,
        100,
        ncities,
        100,
        100,
        1000,
        1000,
        cutoffr)

connect(G_population,cutoffr)
connect(G_resources,cutoffr)

positions   = nx.get_node_attributes(G_population,"pos")

arr_pop,arr_res = evolve(
        G_population,
        G_resources,
        3000,
        0.1,
        0.1,
        0.1)

populations = arr_pop[-1,:]

out = ""
out += "NCITIES, " + str(ncities)
out += "\nCUTOFFR, " + str(cutoffr)
out += "\nINITIALPOP, " + str(100*ncities)
out += "\nFINALPOP, " + str(np.sum(arr_pop, axis = 1)[-1])
out += "\nFAILCITIES, " + str(len(populations[populations < 100]))
out += "\nMEANPOP, " + str(np.mean(populations))

print(out)
