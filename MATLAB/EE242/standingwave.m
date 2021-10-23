function[]=standingwave()
clc;
warning off;
L=input('enter the length of line=');
zl=input('enter the value of load impedance=');
f=input('enter the frequency of operation=');
zo=input('enter the value of char. impedance of line=');
display('reflection coefficient is r=')
r=((zl-zo)/(zl+zo))
display('vswr of line is=')
s=(1+abs(r))./(1-abs(r))
z=linspace(0,L,1000);
figure
hold on
for t=0:0.0001:1
    vf=exp((2*pi*f*t)*j).*exp((-2*pi*z)*j);
    vr=r.*exp(2*pi*f.*t*j)*exp(2*pi.*z*i);
    v=vf+vr;
   plot(z,v,'y',z,vf,'k',z,vr,'m');ylim([-2,2]);
   xlabel('varratioan along line length');
   ylabel('volatage along line');  
end