clc
close all
clear
fs = 1e6;
fsig = 200e3;
t_width = 1e-6;
t = linspace(0,t_width/100*50000,50000);

x = sin(fsig*2*pi*t);
y = x;
current_sample = x(1);

for i = 1:length(t)
    if(mod(i,100)==1)
        i
        t(i)
        current_sample = y(i);
    else
        y(i) = current_sample;
    end
end

f = linspace(-2e6,2e6,20);
Tp1 = 0.25e-6;
Hf1 = Tp1.*sin(pi*f*Tp1)./(pi*f*Tp1).*exp(-1i*pi.*f*Tp1);


freq = linspace(0,length(t)-1,length(t))*0.002/t_width-length(t)*0.002/t_width/2;     
shifted = abs(fftshift(fft(y)));
shifted = shifted/max(shifted);
index_lo= find(freq==-2e6,1,'first');
index_hi= find(freq==2e6,1,'first');

figure
hold on
%plot(t,x)
%plot(t,y)
plot(freq(index_lo:index_hi),shifted(index_lo:index_hi))
plot(f,abs(Hf1)/max(abs(Hf1)),':')
xlabel('frequency(Hz)')
legend('signal spectrum','zero-order hold spectrum')
hold off

%%
clc
clear
close all
f = linspace(-10e6,10e6,200);
t(1:512) = 1;
Tp1 = 0.25e-6;
Tp2 = 0.5e-6;
Tp3 = 1e-6;
Hf1 = Tp1.*sin(pi*f*Tp1)./(pi*f*Tp1).*exp(-1i*pi.*f*Tp1);
Hf2 = Tp2.*sin(pi*f*Tp2)./(pi*f*Tp2).*exp(-1i*pi.*f*Tp2);
Hf3 = Tp3.*sin(pi*f*Tp3)./(pi*f*Tp3).*exp(-1i*pi.*f*Tp3);
figure(1)
hold on
plot(f,abs(Hf1))
plot(f,abs(Hf2))
plot(f,abs(Hf3))
xlabel('frequency (Hz)')
legend(strcat('Pulse width=',num2str(Tp1*1e6),'{\mu}s'),...
    strcat('Pulse width=',num2str(Tp2*1e6),'{\mu}s'),...
    strcat('Pulse width=',num2str(Tp3*1e6),'{\mu}s'))
title('Frequency response of zero-order hold')

