%% EVM Testing
clc;
close all;
clear;

% params
phase_distortion_max = 0.01;% from 0 to 2pi
noise_max_dB = -17;
noise_max = 10^(noise_max_dB/10);
numSym = 5000;
M = 64;
bitsPerSym = log2(M);
x = randi([0 M-1],numSym,1);%(0:M-1)';
y = qammod(x,M,'UnitAveragePower',true);

show_constDiag = 0;
max_input = 1.2;
min_input = 0.1;

input_vect = linspace(min_input,max_input,24);
output_vect_trad = input_vect.* ((input_vect./abs(input_vect) - input_vect*0.2597 + 1.8914*input_vect.^3./abs(input_vect) ...
    - 7.500*input_vect.^3 + 12.902*input_vect.^5./abs(input_vect) - 10.05 *input_vect.^5 ...
    + 2.8799*input_vect.^7./abs(input_vect)));
output_vect_new = input_vect.* ((input_vect./abs(input_vect) - input_vect*0.0102 + 0.3248*input_vect.^3./abs(input_vect) ...
    - 1.8713*input_vect.^3 + 4.1101*input_vect.^5./abs(input_vect) - 3.8768 *input_vect.^5 ...
    + 1.2341*input_vect.^7./abs(input_vect)));
EVM_vect_trad = zeros(size(input_vect));
EVM_vect_new = zeros(size(input_vect));

for ii = 1:length(input_vect)
    y_r = real(y)/max(real(y))*input_vect(ii);
    y_i = imag(y)/max(imag(y))*input_vect(ii);

    norm_mixer = y;
    gmlin_mixer = y;



    % traditional mixer
    trad_mixer_gain_r = (y_r./abs(y_r) - y_r*0.2597 + 1.8914*y_r.^3./abs(y_r) - 7.500*y_r.^3 + 12.902*y_r.^5./abs(y_r) - 10.05 *y_r.^5  + 2.8799*y_r.^7./abs(y_r)); 
    trad_mixer_gain_i = (y_i./abs(y_i) - y_i*0.2597 + 1.8914*y_i.^3./abs(y_i) - 7.500*y_i.^3 + 12.902*y_i.^5./abs(y_i) - 10.05 *y_i.^5  + 2.8799*y_i.^7./abs(y_i));
    trad_mixer_out = abs(y_r) .* trad_mixer_gain_r +1i* abs(y_i) .* trad_mixer_gain_i;
    %trad_mixer_out = trad_mixer_out / max(real(trad_mixer_out)); %normalize gain to 1
    trad_mixer_out = trad_mixer_out * max(real(y)); % rescale to 64 QAM magnitude
    % add noise
    %trad_mixer_out = trad_mixer_out + rand(numSym,1)*noise_max-noise_max/2+1i*(rand(numSym,1)*noise_max-noise_max/2);
    trad_mixer_out = awgn(trad_mixer_out,-noise_max_dB);
    trad_mixer_out = trad_mixer_out .* exp(1i*(rand(numSym,1)*phase_distortion_max-phase_distortion_max));


    %new mixer
    new_mixer_gain_r = (y_r./abs(y_r) - y_r*0.0102 + 0.3248*y_r.^3./abs(y_r) - 1.8713*y_r.^3 + 4.1101*y_r.^5./abs(y_r) - 3.8768 *y_r.^5  + 1.2341*y_r.^7./abs(y_r)); 
    new_mixer_gain_i = (y_i./abs(y_i) - y_i*0.0102 + 0.3248*y_i.^3./abs(y_i) - 1.8713*y_i.^3 + 4.1101*y_i.^5./abs(y_i) - 3.8768 *y_i.^5  + 1.2341*y_i.^7./abs(y_i));
    new_mixer_out = abs(y_r) .* new_mixer_gain_r +1i* abs(y_i) .* new_mixer_gain_i;
    %new_mixer_out = new_mixer_out / max(real(new_mixer_out)); %normalize gain to 1
    new_mixer_out = new_mixer_out * max(real(y)); % rescale to 64 QAM magnitude
    % add noise
    %new_mixer_out = new_mixer_out + rand(numSym,1)*noise_max-noise_max/2+1i*(rand(numSym,1)*noise_max-noise_max/2);
    new_mixer_out = awgn(new_mixer_out,-noise_max_dB);
    new_mixer_out = new_mixer_out .* exp(1i*(rand(numSym,1)*phase_distortion_max-phase_distortion_max/2));

    if (show_constDiag == 1)
        %scatterplot(y)
        %scatterplot(norm_mixer)
        cd1 = comm.ConstellationDiagram('ReferenceConstellation',y*max_input,'ShowReferenceConstellation',true,'Title','Traditional Mixer');
        %step(cd,y);
        cd1(trad_mixer_out);


        cd = comm.ConstellationDiagram('ReferenceConstellation',y*max_input,'ShowReferenceConstellation',true,'Title','New Mixer');
        %step(cd,y);
        cd(new_mixer_out);
    end
    evm = comm.EVM('MaximumEVMOutputPort',true,...
        'XPercentileEVMOutputPort',true, 'XPercentileValue',90,...
        'SymbolCountOutputPort',true);
    [rmsEVM_trad,maxEVM_trad,pctEVM_trad,numSym_trad] = evm(y*input_vect(ii), trad_mixer_out);
    [rmsEVM_new,maxEVM_new,pctEVM_new,numSym_new] = evm(y*input_vect(ii), new_mixer_out);
    EVM_vect_trad(ii) = rmsEVM_trad;
    EVM_vect_new(ii) = rmsEVM_new;
    display(strcat('When max input amplitude =',num2str(input_vect(ii)),...
        'V, RMS EVM (trad) is:',num2str(rmsEVM_trad),...
        '% ,RMS EVM (new) is:',num2str(rmsEVM_new),'%, Max EVM (trad) is: ', ...
        num2str(maxEVM_trad),'%, Max EVM (new) is: ',...
        num2str(maxEVM_new),'%'))
    
    
end

figure(3)
hold on
plot(input_vect,EVM_vect_trad,'b');
plot(input_vect,EVM_vect_new,'r');
legend('traditional','new design')
hold off
title('EVM vs Max Input  Amplitude')
ylabel('EVM (%)')
grid on


figure(4)
hold on
plot(output_vect_trad,EVM_vect_trad,'b');
plot(output_vect_new,EVM_vect_new,'r');
legend('traditional','new design')
hold off
title('EVM vs Max Output  Amplitude')
ylabel('EVM (%)')
xlabel('Max Output Amplitude')

grid on
%%

%y = qammod(x,M,'PlotConstellation',true);
avgPower = mean(abs(y).^2)
z = qamdemod(y,M);

scatterplot(y)
%title('64-QAM, Average Power = 1 W')

cd = comm.ConstellationDiagram('ShowReferenceConstellation',false);
step(cd,txSig)

evm = comm.EVM('MaximumEVMOutputPort',true,...
    'XPercentileEVMOutputPort',true, 'XPercentileValue',90,...
    'SymbolCountOutputPort',true);
[rmsEVM,maxEVM,pctEVM,numSym] = evm(y,txSig)

%input_i = floor(rand(1,10000)*8)-3.5;
%input_q = floor(rand(1,10000)*8)-3.5;


%scatter(input_i,input_q)

%%
close all
y_r = linspace(-1.3,1.3,100);
gain1 = y_r./abs(y_r) - y_r*0.2597 + 1.8914*y_r.^3./abs(y_r) - 7.500*y_r.^3 + 12.902*y_r.^5./abs(y_r) - 10.05 *y_r.^5  + 2.8799*y_r.^7./abs(y_r);
gain1 = gain1/max(gain1)
gain2 = y_r./abs(y_r) - y_r*0.0102 + 0.3248*y_r.^3./abs(y_r) - 1.8713*y_r.^3 + 4.1101*y_r.^5./abs(y_r) - 3.8768 *y_r.^5  + 1.2341*y_r.^7./abs(y_r);
gain2 = gain2/max(gain2)
figure(1)
hold on
%plot(y_r,z1./y_r,'b')
%plot(y_r,z2./y_r,'r')
plot(y_r,y_r.*gain1,'b')
plot(y_r,y_r.*gain2,'r')
plot(y_r,abs(y_r),'g')
%plotyy(mag2db(y_r),mag2db(z1),mag2db(y_r),mag2db(z2))


