clear all
close all
clc

    del_db = linspace(0,2,100);
    del = 10.^(del_db/20)-1;
    del_angle = linspace(0,15,50);
    del_rad = del_angle*3.1415/180;

    IRR = zeros(length(del_angle),length(del));

    for i = 1:length(del_angle)
        for j = 1:length(del)
            IRR(i,j) = 10*log10((del_rad(i)^2+del(j)^2)/4);
        end
    end

    [c,h] = contourf(del_db,del_angle,IRR);

    clabel(c,h,'manual');
    xlabel('20log_{10}|\alpha|')
    ylabel('\Delta{\phi} in degrees')
    title('Contour Map of Constant IRR')