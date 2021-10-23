clc
close all
clear all
Len = 2.5; %meter
Z0 = 75; %Phms
Cp = 138e-12;
Lp = Z0^2*Cp;
c = 1/sqrt(Cp*Lp);
td = Len/c;
t = linspace(-td*0.05,td*1.1*3,200*3);
V = zeros(size(t));
Z_L = 100;

gamma_L = (Z_L-Z0)/(Z_L+Z0);

k = 0;
for i=1:length(t)-1
   display(i)
   if(t(i) <= 0)
       V(i) = 0;
   elseif(t(i)*c < Len/3)
       V(i) = -6/(Len/3/c)*(t(i)-Len/c/3)/3;
   elseif(t(i)*c < Len*2/3)
       V(i) = -4/(Len/3/c)*(t(i)-Len*2/c/3)/3;
   elseif(t(i)*c < Len)
       V(i) = -2/(Len/3/c)*(t(i)-Len/c)/3;
       
   elseif(t(i)*c < Len*4/3)
       V(i) = -2/(Len/3/c)*(t(i)-Len/c*3/3)/(3);
   elseif(t(i)*c < Len*5/3)
       V(i) = -4/(Len/3/c)*(t(i)-Len/c*4/3)/(3);
   elseif(t(i)*c < 2*Len)
       V(i) = -6/(Len/3/c)*(t(i)-Len/c*5/3)/(3);
       
   elseif(t(i)*c < Len*7/3)
       V(i) = -6/(Len/3/c)*(t(i)-Len/c*7/3)/3;
   elseif(t(i)*c < Len*8/3)
       V(i) = -4/(Len/3/c)*(t(i)-Len/c*8/3)/3;
   elseif(t(i)*c < 3*Len)
       V(i) = -2/(Len/3/c)*(t(i)-Len/c*9/3)/3;
   end
    
end
figure
hold on
plot(t*1e9,V)
hold off
title(strcat({'Source Voltage versus Time',' '}))
ylabel('Vs(V)')
xlabel('t(ns)')

%%
clc
close all
clear all
Len = 0.15; %meter
Z0 = 50; %Phms
Cp = 138e-12;
Lp = Z0^2*Cp;
c = 1.5e8;
td = Len/c;
t = linspace(-td*0.5,td*50,500);
V = zeros(size(t));
Z_L = 100;

gamma_L = (Z_L-Z0)/(Z_L+Z0);

k = 1;
V(1) = 1/3;
sum = 0;
for i=2:length(t)
    if(t(i)*c <= Len*2*k)
        V(i) = V(i-1);
    else
       sum = sum + 2*((1-V(i-1))^2/2);
        V(i) = V(i-1)+(1/3)*gamma_L^(k-1)+(1/3)*gamma_L^k;
        V(i)       
        k = k+1;
         
    end
end


for i=1:length(t)
   %display(i)
    if(t(i)*c <= 0)
        V(i) = 0;
    end
end
for i=1:length(t)
   %display(i)
        V(i) = (1-V(i))/2;
end

for i=1:length(t)
   %display(i)
    if(t(i)*c <= 0)
        V(i) = 0;
    end
end


plot(t*1e9,V)
title(strcat({'Source current versus Time',' '}))
ylabel('V_{0}/Z_{0}')
xlabel('t/t_{d}')'

%%
close all
clear all
clc

z = -0.21875:0.001:0;
V_p1 = zeros(length(z));
V_n1 = zeros(length(z));
omega = 1.2e9*2*pi;
v = 3e8/2;
t = 0;
beta = omega/v;
zl = 150;
z0 = 50;
zs = 5;
gamma_L = (zl-z0)/(zl+z0);
gamma_S = (zs-z0)/(zs+z0);
zin = z0^2/zl;


figure(1)
for t = linspace(0,2*pi/omega*100,30)    
    V_p1 = (zin)/(zin+zs)*sin(omega*t-beta*z);
    V_n1 = (zin)/(zin+zs)*gamma_L*sin(omega*t+beta*z);
    V_p2 = (zin)/(zin+zs)*gamma_L*gamma_S*sin(omega*t-beta*z);
    V_n2 = (zin)/(zin+zs)*gamma_L*gamma_S*gamma_L*sin(omega*t+beta*z);
    Vss = V_p1+V_n1+V_p2+V_n2;
    pause(0.1)
    hold on
    plot(z*1000,Vss)
    axis([z(1)*1000,0,-3,3])
end
xlabel('z(mm)')
ylabel('V(V)')
title('voltage on the T-Line vs z for different t')