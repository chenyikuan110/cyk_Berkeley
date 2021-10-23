clc
clear all
close all

dummy = importdata('ramp_ref_256.txt');
bitsumV_X = dummy.data(:,1);
bitsumV_Y = dummy.data(:,2);

dummy = importdata('ramp_mix_256.txt');
Vmix_outV_Y = dummy.data(:,2);
Vmix_outV_Y_norm_align = Vmix_outV_Y-min(Vmix_outV_Y(1:1000));
Vmix_outV_Y_norm_align = Vmix_outV_Y_norm_align/max(Vmix_outV_Y_norm_align);

neg_Vmix = -Vmix_outV_Y_norm_align+max(Vmix_outV_Y_norm_align);

ref_Y = bitsumV_Y/max(bitsumV_Y);

figure(1)
hold on
plot(ref_Y)
plot(Vmix_outV_Y_norm_align)
hold off

[mix_peaks_p,mix_peaks_locs_p] = findpeaks(neg_Vmix);
[mix_peaks_n,mix_peaks_locs_n] = findpeaks(Vmix_outV_Y_norm_align);
len_peaks = min(length(mix_peaks_p),length(mix_peaks_n));

mix_peaks = zeros(1,len_peaks);
mix_peaks_locs = zeros(1,len_peaks);

% make sure the phase is correct
for i=1:len_peaks
    if(ref_Y(mix_peaks_locs_p(i)) < max(ref_Y)/2)
        mix_peaks(i)= -mix_peaks_p(i)+1;
        mix_peaks_locs(i) = mix_peaks_locs_p(i);
    else
        mix_peaks(i)= mix_peaks_n(i);
        mix_peaks_locs(i) = mix_peaks_locs_n(i);       
    end
end
mix_norm = mix_peaks;

figure(9)
hold on
plot(mix_peaks_locs,mix_peaks)
plot(Vmix_outV_Y_norm_align)
hold off

% normalize the sample
mix_aligned = (mix_norm - min(mix_norm));
mix_aligned = mix_aligned/max(mix_aligned);

mix_peaks_aligned = mix_peaks - min(mix_peaks);
mix_peaks_aligned = mix_peaks_aligned/max(mix_peaks_aligned);

ref_Y_final = ref_Y(mix_peaks_locs);
[a,b] = find(ref_Y_final==max(ref_Y_final));

endpoint = a(length(a));
ref_Y_final = ref_Y_final(2:endpoint);
ref_Y_final = ref_Y_final-min(ref_Y_final);
ref_Y_final = ref_Y_final/max(ref_Y_final);

mix_peaks_final = mix_peaks_aligned(2:endpoint);
mix_peaks_final = mix_peaks_final-min(mix_peaks_final);
mix_peaks_final = mix_peaks_final/max(mix_peaks_final);

sampled_locs = zeros(1,endpoint-1);

for i=2:endpoint
    sampled_locs(i-1) = mix_peaks_locs(i);
end
   

mix_peaks_interp = zeros(1,sampled_locs(length(sampled_locs)-1));
ref_Y_interp = mix_peaks_interp;

% for all the sampled point but the last one, interpolate (unevenly)
for i=1:(length(sampled_locs)-1)
    for k = sampled_locs(i):sampled_locs(i+1)-1
        mix_peaks_interp(k) = mix_peaks_final(i);
        ref_Y_interp(k) = ref_Y_final(i);
    end
end

figure(2)
hold on
plot(ref_Y_interp);
plot(mix_peaks_interp);
hold off

% data preparation done
%% above is data preparation

% EVM starting below
close all
clc
for N_QAM = [16 64 256 1024]
    N = sqrt(N_QAM);
    numSym = N_QAM*100;
    % reference values
    ideal_level = linspace(0,1,N);

    % sequence generation
    seq_r = randi([0 N-1],1,numSym);
    seq_i = randi([0 N-1],1,numSym);

    % mapping to the data sequence we prepared above
    % to generate a normalized constellation diagram
    sample_r = round((seq_r)/N*length(ref_Y_interp))+1;
    sample_i = round((seq_i)/N*length(ref_Y_interp))+1;

    % randomize a bit...
    for i=1:numSym
        valid_index_r = find(ref_Y_interp==ref_Y_interp(sample_r(i)));
        sample_r(i) = randi([valid_index_r(1) valid_index_r(length(valid_index_r))]);
        valid_index_i = find(ref_Y_interp==ref_Y_interp(sample_i(i)));
        sample_i(i) = randi([valid_index_i(1) valid_index_i(length(valid_index_i))]);    
    end
   
    figure()
    set(gcf, 'Position',  [100, 100, 600, 600])
    hold on
    scatter(2*ref_Y_interp(sample_r)-(N-1)/N,2*ref_Y_interp(sample_i)-(N-1)/N)
    scatter(2*mix_peaks_interp(sample_r)-(N-1)/N,2*mix_peaks_interp(sample_i)-(N-1)/N,'.')
    hold off
    title(strcat(num2str(N_QAM),'-QAM Constellation'))

    % EVM calculation
    numerator = 0;
    denominator = 0;
    for i = 1:numSym
        % Error vector 
        square_dist = (ref_Y_interp(sample_r(i))-mix_peaks_interp(sample_r(i)))^2 ...
            + (ref_Y_interp(sample_i(i))-mix_peaks_interp(sample_i(i)))^2;    
        square_ref_mag =  (ref_Y_interp(sample_r(i))-0.5)^2 + (ref_Y_interp(sample_i(i))-0.5)^2;

        numerator = numerator + square_dist;
        denominator = denominator + square_ref_mag;
    end
    %numerator = numerator/numSym;
    %denominator = denominator/numSym;

    myEVM = sqrt(numerator/denominator);
    
    pw=denominator*0.35^2/0.5^2/2/100/numSym;
    pw = 10*log10(pw*1000);
    display(strcat(num2str(N_QAM),'-QAM: EVM is =',num2str(myEVM*100),'%, or =',num2str(20*log10(myEVM)),'dB'));
    display(strcat('Average power is=',num2str(pw),'dBm'));
end

