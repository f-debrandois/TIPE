import numpy as np
import numpy.linalg as LA

# Agent class
class Agent:
    def __init__(self, position, exit, v0, radius, mass, tau):
        self.position = position
        self.exit = exit
        self.v0 = v0
        self.radius = radius
        self.mass = mass
        self.tau = tau
        self.speed = self.f_DesiredSpeed()

    def f_DesiredDirection(self):
        return (self.exit - self.position) / LA.norm(self.exit - self.position)

    def f_DesiredSpeed(self):
        return self.f_DesiredDirection() * self.v0

# Wall Class
class Wall:
    def __init__(self, ext1, ext2):
        self.ext1 = ext1
        self.ext2 = ext2

    # Return the closest point of the wall from a given point
    def wallDistance(self, point):
        temp = np.dot(point - self.ext1, self.ext2 - self.ext1) / (LA.norm(self.ext2 - self.ext1))**2
        temp = min( max(0, temp), 1 )
        proche = self.ext1 + (self.ext2 - self.ext1)*temp
        return proche


# Motion class
class Motion:
    def __init__(self):
        self.A = 2*10**3
        self.B = 0.08
        self.k = 1.2*10**5
        self.kap = 2.4*10**5

    def g(self, x):
        if x < 0:
            return 0
        return x

    # Force between two agents
    def f_AgentsIJ(self, agentI, agentJ):
        d = LA.norm(agentI.position - agentJ.position)
        n = (agentI.position - agentJ.position)/d
        t = np.array([-n[1], n[0]])
        r_tot = agentI.radius + agentJ.radius
        dv_t = np.dot(agentJ.speed - agentI.speed, t)

        a = (self.A * np.exp((r_tot - d)/self.B)) + (self.k * self.g(r_tot - d))
        b = self.kap * self.g(r_tot - d) * dv_t

        return a*n + b*t

    # Forces between all agents
    def f_Agents(self, agents):
        F_total = np.zeros((len(agents), 2))
        for i in range(len(agents)):
            for j in range(i):
                F = self.f_AgentsIJ(agents[i], agents[j])
                F_total[i, :] += F
                F_total[j, :] -= F
        return F_total

    # Force between an agent and a wall
    def f_AgentIWallJ(self, agentI, wallJ):
        point = wallJ.wallDistance(agentI.position)
        d = LA.norm(agentI.position - point)
        n = (agentI.position - point) / d
        t = np.array([-n[1], n[0]])
        r_tot = agentI.radius
        dv_t = -np.dot(agentI.speed, t)

        a = (self.A * np.exp((r_tot - d)/self.B)) + (self.k * self.g(r_tot - d))
        b = self.kap * self.g(r_tot - d) * dv_t

        return a*n + b*t

    # Force all agents and all walls
    def f_Walls(self, agents, walls):
        F_total = np.zeros((len(agents), 2))
        for i in range(len(agents)):
            for j in range(len(walls)):
                F = self.f_AgentIWallJ(agents[i], walls[j])
                F_total[i, :] += F
        return F_total

    # Acceleration of each agents
    def acceleration(self, agents, walls):
        a = np.zeros((len(agents), 2))
        F_Agents = self.f_Agents(agents)
        F_Walls = self.f_Walls(agents, walls)

        for i in range(len(agents)):
            v0e0 = agents[i].f_DesiredSpeed()
            a[i, :] = ((v0e0 - agents[i].speed)/agents[i].tau) + (F_Agents[i, :]/agents[i].mass) + ((F_Walls[i, :])/agents[i].mass)

        return a

    # Update of speed and position
    def euler(self, agents, walls, dt):
        a = self.acceleration(agents, walls)
        for i in range(len(agents)):
            agents[i].speed =  agents[i].speed + dt * a[i]
            agents[i].position = agents[i].position + dt * agents[i].speed
