clc
clear
close all

Nc = 2.8e25; % unit 1/m^3

mu_n= 0.03678;%m^2/(V*s)
W= 1e-5;%m
Cox= 0.003453;% F/m2
L=2e-6;%m

VG1 = 2;%V
VG2 = 3; %V
VG3 = 4;%V
VT = 1.0267;%V

VD = linspace(0,5,44);

ID1= VD;
ID2= VD;
ID3= VD;


for i=1:length(VD)
    if(VD(i)<= (VG1-VT))
        ID1(i) = mu_n*W*Cox/L*((VG1-VT)*VD(i)-VD(i)^2/2);
    else
        ID1(i) = mu_n*W*Cox/L/2*((VG1-VT)^2);
    end
    
    if(VD(i)<= (VG2-VT))
        ID2(i) = mu_n*W*Cox/L*((VG2-VT)*VD(i)-VD(i)^2/2);
    else
        ID2(i) = mu_n*W*Cox/L/2*((VG2-VT)^2);
    end
   
    if(VD(i)<= (VG3-VT))
        ID3(i) = mu_n*W*Cox/L*((VG3-VT)*VD(i)-VD(i)^2/2);
    else
        ID3(i) = mu_n*W*Cox/L/2*((VG3-VT)^2);
    end
    
end
%set(gca, 'XScale', 'log')
figure(1);
grid on
hold on
plot(VD,ID1);
plot(VD,ID2);
plot(VD,ID3);
ylabel('I_D(A)')
xlabel('V_D(V)')
title('I_D vs V_D')
legend('V_G=2V','V_G=3V','V_G=4V')

