# -*- coding: utf-8 -*-
"""
Created on Mon Mar  4 11:35:24 2019

@author: afas9
"""


from matplotlib import pyplot as plt
import os


# Define the file path dynamically
file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Files', 'Results.txt'))

# Check if the file exists
if not os.path.exists(file_path):
    raise FileNotFoundError(f"File not found: {file_path}")

# Open and read the file
with open(file_path, 'r') as f:
    mensaje = f.read()

text = mensaje.splitlines()
linea = text[0].split()
numManholes = int(linea[1])
manholes = numManholes    # Set the number of manholes


idd = []
inflow = []
posX = []
posY = []
posZ = []
arcs = []

for i in range(numManholes):
    linea = text[i + 1].split()
    idd.append(int(linea[0]))
    posX.append(float(linea[1]))
    posY.append(float(linea[2]))
    posZ.append(float(linea[3]))

    
linea = text[numManholes + 1].split()
numSections = int(linea[1])

for i in range(numSections):
    linea = text[numManholes + i + 2].split()
    idManUp = int(linea[0])
    idManDown = int(linea[1])
    type = int(linea[2])
    ar = (idManUp, idManDown, type)
    arcs.append(ar)
   

ax = plt.axes()

for i in range(manholes-1):
    ax.plot(posX[i], posY[i],  marker='o', markersize=1, color="g",label=i)
    plt.annotate(str(i+1), (posX[i],posY[i]+5),size=6)
    
ax.plot(posX[-1], posY[-1],  marker='P', markersize=3, color="k",label=i)
plt.annotate(str(i+1), (posX[i],posY[i]+5),size=6)
    
head = 10 #Tanaño de la cabeza de la flecha

for i, j, t in arcs:
    #print(str(i)+" "+str(j)+" "+str(t))
    if i >= len(posX) or j >= len(posX):
        print(f"Invalid indices: i={i}, j={j}, skipping this arc.")
        continue
    
    dx = posX[j]-posX[i]
    dy = posY[j]-posY[i]
    m = abs(dx / dy)
    if dx == 0 or dy == 0:
        m = 0


    l = 10.0
    ty = ((l**2)/(m+1))**0.5
    tx = m*ty

    if t==1:
        if dx<0 and dy<0:
           ax.arrow(posX[i],posY[i],dx+2*tx,dy+2*ty,head_width=head,fc='r', ec='r')
           
        elif dx<0 and dy>0:
            ax.arrow(posX[i],posY[i],dx+tx,dy-ty,head_width=head,fc='r', ec='r')
        elif dx>0 and dy<0:
            ax.arrow(posX[i],posY[i],dx-tx,dy+ty,head_width=head,fc='r', ec='r')
        elif dx>0 and dy>0:
            ax.arrow(posX[i],posY[i],dx-tx,dy-ty,head_width=head,fc='r', ec='r')
    else:
        if dx<0 and dy<0:
            ax.arrow(posX[i],posY[i],dx+tx,dy+ty,head_width=head,fc='b', ec='b')
        elif dx<0 and dy>0:
            ax.arrow(posX[i],posY[i],dx+tx,dy-ty,head_width=head,fc='b', ec='b')
        elif dx>0 and dy<0:
            ax.arrow(posX[i],posY[i],dx-tx,dy+ty,head_width=head,fc='b', ec='b')
        elif dx>0 and dy>0:
            ax.arrow(posX[i],posY[i],dx-tx,dy-ty,head_width=head,fc='b', ec='b')
                
#ax.arrow(0.5,0.2,,-0.1,head_width=0.1,fc='b', ec='r')
#ax.arrow(0,0,0.5,1,head_width=0.1,fc='b', ec='r

    

img=plt.savefig("Red.jpg",dpi=1000)


plt.show()


