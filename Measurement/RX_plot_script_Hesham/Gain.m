close all; clear all; clc;

debug=1;

d = 0.3;
freq_min = 110;
freq_max = 170;

my_dir = "C:\Users\Hesham\Desktop\My Drive\My Work\Berkeley\Group\measured_data\radar\RX\";
my_subdir = "";
atten_value = "atten_1.00";

freq_rec_power = [];
rec_power = [];
fig_legend = [];

file=sprintf('%s%sextender_power.xlsx',my_dir,my_subdir);
tmp=table2array(readtable(file))';
freq_ref_power_course=tmp(1,:);
ref_power_course = tmp(2,:);

file=sprintf('%s%sOE_gain.csv',my_dir,my_subdir);
tmp=table2array(readtable(file))';
freq_oe_gain=tmp(1,:);
oe_gain_smooth = tmp(2,:);
oe_gain_actual = tmp(3,:);

file=sprintf('%s%shorn_gain.csv',my_dir,my_subdir);
tmp=table2array(readtable(file))';
freq_horn_gain=tmp(1,:);
horn_gain_smooth = tmp(2,:);
horn_gain_actual = tmp(3,:);

my_subdir="Atten\";

file=my_dir+my_subdir+atten_value+".csv";
tmp=table2array(readtable(file))';
freq_atten=tmp(1,:)/1e9;
atten = tmp(2,:);

freq = freq_min:0.25:freq_max;

fspl = -20*log10(d*freq*10*4*pi/3);
ref_power = interp1(freq_ref_power_course,ref_power_course,freq,'makima');
oe_gain = interp1(freq_oe_gain,oe_gain_actual,freq,'makima');
horn_gain = interp1(freq_horn_gain,horn_gain_actual,freq,'makima');
atten = interp1(freq_atten,atten,freq,'makima');

eirp = ref_power+horn_gain+fspl+atten;


        my_subdir="";
        file=sprintf('%s%sRX_RF.csv',my_dir,my_subdir);
        tmp=table2array(readtable(file));
        freq_rec_rx=tmp(1,:);
        rec_rx = tmp(3,:);   



        gain = rec_rx-interp1(freq,eirp,freq_rec_rx,'makima')+3;
        
        figure(1);
        hold on

        plot(freq_rec_rx,gain)
        plot(freq_rec_rx,movmean(gain,5))

figure(1);
xlabel('Freq [GHz]');
ylabel('Receiver OTA Gain [dB]');
pbaspect([2 2 1])
grid on
% xlim([115 155]);
% ylim([-65 -50]);
% xticks(115:5:155);
% yticks(-64:2:-50);
% legend(fig_legend,'fontsize',12,'location','southwest');
% title('at 30cm Ref.');

clc;
