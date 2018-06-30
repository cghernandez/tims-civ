import networkx as nx
import matplotlib.pyplot as plt
import random
import scipy.sparse as sp
import numpy as np
import sys

#Read number of cities to create, and cutoff radius, as 
#command line parameters

ncities = int(sys.argv[1])
cutoffr = int(sys.argv[2])

#This function receives the map dimensions, number of cities,
#a range for initial population, a range for initial resources 
#and a cutoff radius. It returns the population and resource graphs.

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

        #If a city location is occupied, pick another

        if (x,y) in usados:
            continue

        r2 = r**2

        #Here any location that is out of reach of any
        #other city is discarded.

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

#This function connects cities by adding edges to the graphs.
#It is implemented so that resource and population graphs have
#the same connections.

def connect(G,r):
    r2 = r**2
    
    for i in range(len(G)):
        
        for j in range(len(G)):

            if i == j:
                continue

            #Cities are connected if their distance is less than the cutoff
            #radius.

            d2 = ((G.nodes[i]["pos"][0] - G.nodes[j]["pos"][0])**2 + 
                    (G.nodes[i]["pos"][1] - G.nodes[j]["pos"][1])**2)

            if d2 < r2:

                #The initial weight of the edge is a function of the distance
                #between the cities. It decreases quadratically as d2
                #increases

                w = (1 - d2/r2)**2

                #At time t0, the weight w and the initial weight w0
                #are the same.

                G.add_edge(i, j, weight = w)
                G[i][j]["weight0"] = w

#This function updates the weights of the population and resource graph
#edges.

def update_weights(G_pop,G_res):

    for i,j in G_pop.edges():

        #Here the resource per capita for city "i"
        #and for city "j" are calculated. Factor 0.01 is included to prevent
        #any singularity from happening.

        ipc = G_res.nodes[i]["res"]/(G_pop.nodes[i]["pop"] + .01)
        jpc = G_res.nodes[j]["res"]/(G_pop.nodes[j]["pop"] + .01)

        #Here the weights are updated, by multiplying the initial weight shown
        #before in "connect(G,r)" by a factor that depends on resource per
        #capita. First, the RPC of both cities are summed, and then
        #the fraction of net RPC that each city holds is calculated.
        #People tend to flow to the city that has the bigger fraction, and
        #resources tend to flow the other way around. 

        G_pop[i][j]["weight"] = G_pop[i][j]["weight0"]*jpc/(ipc + jpc + 0.01)
        G_res[i][j]["weight"] = G_res[i][j]["weight0"]*ipc/(ipc + jpc + 0.01)

#This function governs the time evolution of the system.

def evolve(G_pop, G_res, steps, gamma, r, k):

    #These are arrays that will hold the state of the population
    #and resource vectors on each timestep.

    state_pop = np.zeros((steps,len(G_pop)))
    state_res = np.zeros((steps,len(G_res)))

    lerate = np.array(list(
        nx.get_node_attributes(G_res,"e_rate").values()))

    for t in range(steps):

        #First, the laplacian matrix of the graphs are calculated. As
        #networkx doesn't have an appropiate function for directed
        #weighted graphs, the construction must be made manually.
        #Notice that the adjacency matrix is transposed, this ensures
        #that the weights of the matrices are well placed according to 
        #"connect" function.

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
        
        #Here the equations are solved

        dlpop = -gamma*L_pop.dot(lpop) + r*lpop*(1 - lpop/(k*(lres + 0.01)))
        dlres = -gamma*L_res.dot(lres) + 0.04*lerate - 0.02*lpop

        lpop = lpop + dlpop
        lres = lres + dlres

        #Negative numbers for population and resources are meaningless, so they
        #are discarded and set to 0.

        lpop[lpop < 0] = 0
        lres[lres < 0] = 0

        nx.set_node_attributes(G_pop,dict(enumerate(lpop)),"pop")
        nx.set_node_attributes(G_res,dict(enumerate(lres)),"res")
 
        #Update weights according to the rules.
        
        update_weights(G_pop,G_res)

    #When the simulation finishes, the last saved state is cast to integer,
    #so that final population and resources are set to integers. This is not
    #done during the simulation as decimals account for small/slow movement of
    #people and resources, so doing it would eliminate that behaviour.

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
