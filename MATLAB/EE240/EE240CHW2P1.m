clc
clear
close all
adc_data = load('hw2_p1_data.mat')
y = adc_data.adc_data;

w = linspace(1,length(y),length(y));
omega = w/length(y)*2*pi;
freq = omega/2/pi*25e6;
y_fft = fft(y);
y_fft_norm_mag = abs(y_fft)/max(abs(y_fft));


plot(freq(1:length(y)/2),mag2db(y_fft_norm_mag(1:length(y)/2)))
title('Spectrum of the sampled data')
xlabel('MHz')
ylabel('dBFS')




snr_y = snr(y)
sinad_y = sinad(y)
sfdr_y = sfdr(y)
thd_y = thd(y)
enob_y = ((sinad(y)-1.76)/6.02)


%%
clc
clear all
close all

Bt = linspace(0,12,13);
B = 12;

Aunit =((8192./(2.^Bt))-1)/42.056;
A_digit = 2.^Bt*200;
A_DAC = 2^B * Aunit;

A_total = A_digit+A_DAC;

figure(1)
hold on
plot(Bt,log10(A_total/1e6),'b','LineWidth',2)
plot(Bt,log10(A_digit/1e6),'c','LineWidth',2)
plot(Bt,log10(A_DAC/1e6),'r','LineWidth',2)
plot(Bt,log10((1.5217*ones(1,13)/1e6)),'LineWidth',2)
hold off
hold on
scatter(Bt,log10(A_total/1e6),'b')
scatter(Bt,log10(A_digit/1e6),'c')
scatter(Bt,log10(A_DAC/1e6),'r')
scatter(0,0)
hold off
legend('Total area','Decoder area','DAC area','worst case A_{INL=2} for 99% yield')
ylabel('log_{10}(Area in mm^2)')
xlabel('B_t')
title('Area vs B_t')