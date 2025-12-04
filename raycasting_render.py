import pygame as pg
import sys
import math
import numpy as np
from pathlib import Path
pg.init()
width=1200
height=400
screen = pg.display.set_mode((width, height))


file = Path("lines.npy")

def load_walls(path: Path):
    if not path.exists():
        return []   
    arr = np.load(path)  
    walls = [[(int(a[0]), int(a[1])), (int(b[0]), int(b[1]))] for a, b in arr]
    
    return walls

walls = load_walls(file)
def check_lineseg(walls, ray):
    inter_array=[]
    ray_slope=math.tan(math.radians(ray[0]))
    if(ray_slope==0):ray_slope=0.000001

    ray_stpos=ray[1]
    ray_int=-ray_slope*ray_stpos[0]+ray_stpos[1]
    ray_en =[ray_stpos[0] + math.cos(math.radians(ray[0]))*ray[2],
            ray_stpos[1] + math.sin(math.radians(ray[0]))*ray[2]]
    #ray: y = ray_slope*x+ray_int
    for wall in walls:
        
        wall_slope= (wall[1][1]-wall[0][1])/(wall[1][0]-wall[0][0])
        wall_stpos=wall[0]
        wall_int = -wall_slope*wall_stpos[0] + wall_stpos[1]
        #wall: y = wall_slope*x + wall_int
        intersectionx=(wall_int-ray_int)/(ray_slope-wall_slope)
        intersectiony=ray_slope* intersectionx+ray_int
        inter=(intersectionx,intersectiony)
        dist_ray1=math.hypot((inter[0]-ray_stpos[0]), (inter[1] - ray_stpos[1]))
        dist_ray2=math.hypot((ray_en[0]-inter[0]), (ray_en[1]-inter[1]))

        dist_wall1=math.hypot((inter[0] - wall[0][0]), (inter[1] - wall[0][1]))
        dist_wall2=math.hypot((inter[0] - wall[1][0]), (inter[1] - wall[1][1]))
        wall_len=math.hypot((wall[0][0]-wall[1][0]), (wall[0][1]- wall[1][1]))
        if(dist_ray1<ray[2] and dist_ray2<ray[2] and dist_wall1<wall_len and dist_wall2<wall_len):
            inter_array.append(inter)
        else: inter_array.append(-1)
    valid_inter_array_dist=[]
    valid_inter_array_cords=[]
    for i in inter_array:
        if(i!=-1):
            valid_inter_array_dist.append(math.hypot((i[0]- ray_stpos[0]),
                                                      (i[1]- ray_stpos[1])))
            valid_inter_array_cords.append(i)
    if(ray[0]==90):print(inter_array)
    if(valid_inter_array_dist):
        mini_dist=min(valid_inter_array_dist)
        i=0
        for dist in valid_inter_array_dist:
            if(mini_dist == dist): 
                idx=i
                break
            i+=1
        return valid_inter_array_cords[idx],mini_dist
    else :return -1,-1
clock = pg.time.Clock()
xpos=100
ypos=200
x_vel=0
y_vel=0
g=0.00
r=300
pos=[xpos,ypos]
drag=0
curr_dirc=0
fov=60
offset=600
rect_width=(width-offset)/fov
prev_mouse_pos=None
mouse_scale=2
step_size=4
while True:
    mousex,mousey=pg.mouse.get_pos()
    if prev_mouse_pos:
        mouse_velvec_x=mousex-prev_mouse_pos[0]
        print(mouse_velvec_x)
        curr_dirc+=mouse_velvec_x/mouse_scale
    keys = pg.key.get_pressed()
    if keys[pg.K_w]:
        pos[0]+=step_size*math.cos(math.radians(curr_dirc))
        pos[1]+=step_size*math.sin(math.radians(curr_dirc))
    for e in pg.event.get():
        if e.type == pg.QUIT: pg.quit(); sys.exit()
        if (e.type == pg.MOUSEBUTTONDOWN and mousex<=pos[0]+6 and mousex>pos[0]-6
         and mousey<=pos[1]+6 and mousey>pos[1]-6):
            drag=1
        if(e.type == pg.MOUSEBUTTONUP):
            drag=0
    
    if drag:
        pos[0]=mousex
        pos[1]=mousey
    
    screen.fill((0, 0, 0))
    pg.draw.circle(screen, (255,255,0),pos,4.0)
    pg.draw.line(screen,(255,255,255),(600,0),(600,400))
    y_vel+=g
    pos[1]+=y_vel
    for wall in walls :
        pg.draw.line(screen, (255,0,255),wall[0], wall[1],2)
    pg.draw.circle(screen,(0,0,255),(10,10),5)
    temp=[]
    x_pos_rect_arr=[]
    for theta in range(int(curr_dirc-fov/2),int(curr_dirc+fov/2),1):
        theta_mapped=theta-(curr_dirc-fov/2)
        temp.append(theta_mapped)
        #print(temp)
        if (abs(theta) == 90 or abs(theta) == 270):continue
    #ray=[theta, (st_pos), length]
        inter,mini_dist = check_lineseg(walls, [theta, pos, r])
        if(inter!=-1):
            red_val=255-(255*mini_dist)/r
            blue_val=(255*mini_dist)/r
            pg.draw.circle(screen,(0,255,0),(int(inter[0]),int(inter[1])),2)
            pg.draw.line(screen,(red_val,0,blue_val),pos,
                     (int(inter[0]), int(inter[1])))
        else :
            pg.draw.line(screen,(255,255,255),pos,
                    (pos[0]+r*math.cos(math.radians(theta)), pos[1]+r*math.sin(math.radians(theta))))
        if(mini_dist == -1):mini_dist=r
        rect_height=height*pow(2,(-mini_dist/r))#expo fuction 
        rect_height=150+250*((300-mini_dist)/r)#
        rect_clr=255*pow(2,3.5*(-mini_dist/r))
        
        x_pos_rect_arr.append(theta_mapped*rect_width+offset)
        pg.draw.rect(screen,(rect_clr,rect_clr,rect_clr),(theta_mapped*rect_width+offset, height/2-rect_height/2, rect_width, rect_height))
    #print(x_pos_rect_arr)
    prev_mouse_pos=(mousex,mousey)
    pg.display.flip()
    clock.tick(30)
